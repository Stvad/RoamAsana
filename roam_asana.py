from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from sys import argv
from typing import *

from dataclasses_json import dataclass_json
from functional import seq


# Roam Schema is here: https://roamresearch.com/#/v8/help/page/RxZF78p60
# For Asana, I just looked at the export result

@dataclass
class Block:
    string: str
    children: List[Block] = field(default_factory=list)


@dataclass_json
@dataclass
class Page:
    title: str
    children: List[Block]


@dataclass
class Task:
    task_json: dict

    def as_block(self) -> Block:
        return Block(self.roam_name(), self.children())

    def name(self):
        return self.task_json['name']

    def roam_name(self):
        return "{{[[DONE]]}} " + self.name() if self.task_json['completed'] else self.name()

    def section(self, separator='|'):
        """If tasks is in multiple Asana sections - combine them into an aggregate section connected by separator"""
        return seq(self.task_json['memberships']).map(lambda it: it['section']['name']).make_string(separator)

    def children(self):
        def description():
            notes = self.task_json['notes']
            return [Block(notes)] if notes else []

        def bracket_estimate(estimate_property="asana_pomodoro_estimate"):
            bracket_number = get_bracket_number(self.name())
            return [Block(f"{estimate_property}::{bracket_number}")] if bracket_number else []

        def due_date_tag():
            return [custom_strftime('%B {S}, %Y', datetime.fromisoformat(self.task_json['due_on']))] \
                if self.task_json['due_on'] else []

        def tags():
            tag_names = seq(due_date_tag()) + seq(self.task_json['tags']).map(lambda it: it['name'])
            tag_str = tag_names.map(lambda it: f"[[{it}]]").make_string(' ')
            return [Block(tag_str)] if tag_str else []

        return tags() + bracket_estimate() + description() + convert_tasks(self.task_json['subtasks'])


def get_bracket_number(string):
    # support for bracket estimates: https://github.com/Stvad/Asana-counter
    regex = '\[([-+]?(\d+|\d+\.\d+))]'
    match = re.search(regex, string)
    if match:
        return match.group(1)
    return None


def custom_strftime(date_format, date):
    def suffix(day):
        return 'th' if 11 <= day <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')

    return date.strftime(date_format).replace('{S}', str(date.day) + suffix(date.day))


def convert_tasks(tasks):
    return (seq(tasks).map(process_task).group_by_key()
            .flat_map(extract_sections).to_list())


def process_task(task_json):
    task = Task(task_json)
    return task.section(), task.as_block()


def extract_sections(block_pair):
    section_name, blocks = block_pair
    if (not section_name) or section_name == "(no section)":
        return blocks
    return [Block(section_name, blocks)]


def main():
    """Usage roam_asana asana_export.json roam.json"""
    input_path = Path(argv[1])
    asana = json.load(input_path.open())

    root_page = Page(input_path.stem, convert_tasks(asana['data']))
    json_str = root_page.to_json(indent=2)
    print(json_str)

    Path(argv[2]).write_text(f"[{json_str}]")


if __name__ == '__main__':
    main()
