from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from pprint import pprint
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


def main():
    """Usage roam_asana asana_export.json roam.json"""
    input_path = Path(argv[1])
    asana = json.load(input_path.open())

    root_page = Page(input_path.stem, convert_tasks(asana['data']))
    # print(root_page)
    pprint(root_page.to_json())
    # pprint(Page.schema().dump([root_page], many=True))
    # Page.schema().dump([root_page], Path(argv[2]).open(mode="w"))
    Path(argv[2]).write_text(f"[{root_page.to_json()}]")


def roam_string(task_json):
    result = task_json['name']
    if task_json['completed']:
        result = "{{[[DONE]]}} " + result
    return result


def convert_tasks(tasks):
    def process_task(task_json):
        # section as tag? or as a parent?
        # maybe square bracket estiamate into the attribute?
        return Block(roam_string(task_json), extract_children(task_json))

    def extract_children(task_json):
        children = convert_tasks(task_json['subtasks'])

        if task_json['notes']:
            children.insert(0, Block(task_json['notes']))

        if task_json['tags']:
            tags = seq(task_json['tags']).map(lambda it: f"[[{it['name']}]]").make_string(' ')
            children.insert(0, Block(tags))

        return children

    return seq(tasks).map(process_task).to_list()


if __name__ == '__main__':
    main()
