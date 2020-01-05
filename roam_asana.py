from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from pprint import pprint
from sys import argv
from datetime import datetime
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


def main():
    """Usage roam_asana asana_export.json roam.json"""
    input_path = Path(argv[1])
    asana = json.load(input_path.open())

    root_page = Page(input_path.stem, convert_tasks(asana['data']))
    pprint(root_page.to_json())
    Path(argv[2]).write_text(f"[{root_page.to_json()}]")


def roam_string(task_json):
    result = task_json['name']
    if task_json['completed']:
        result = "{{[[DONE]]}} " + result
    return result


def process_task(task_json):
    # maybe square bracket estiamate into the attribute?
    return task_section(task_json), Block(roam_string(task_json), extract_children(task_json))


def task_section(task_json, separator='|'):
    """If tasks is in multiple Asana sections - combine them into an aggregate section connected by separator"""
    return seq(task_json['memberships']).map(lambda it: it['section']['name']).make_string(separator)


def get_bracket_number(task_name):
    # support for bracket estimates: https://github.com/Stvad/Asana-counter
    regex = '\[([-+]?(\d+|\d+\.\d+))]'
    match = re.search(regex, task_name)
    if match:
        return match.group(1)
    return None


def custom_strftime(date_format, date):
    def suffix(day):
        return 'th' if 11 <= day <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')

    return date.strftime(date_format).replace('{S}', str(date.day) + suffix(date.day))


def extract_children(task_json):
    def bracket_estimate(estimate_property="asana_pomodoro_estimate"):
        bracket_number = get_bracket_number(task_json['name'])
        return [Block(f"{estimate_property}::{bracket_number}")] if bracket_number else []

    def notes():
        return [Block(task_json['notes'])] if task_json['notes'] else []

    def due_date_tag():
        return custom_strftime('[[%B {S}, %Y]]', datetime.fromisoformat(task_json['due_on'])) \
            if task_json['due_on'] else ''

    def tags():
        tag_str = due_date_tag() + ' ' + seq(task_json['tags']).map(lambda it: f"[[{it['name']}]]").make_string(' ')
        return [Block(tag_str)] if tag_str else []

    return tags() + bracket_estimate() + notes() + convert_tasks(task_json['subtasks'])


def convert_tasks(tasks):
    return (seq(tasks).map(process_task).group_by_key()
            .flat_map(section_blocks).to_list())


def section_blocks(block_pair):
    section_name, blocks = block_pair
    if (not section_name) or section_name == "(no section)":
        return blocks
    return [Block(section_name, blocks)]


if __name__ == '__main__':
    main()
