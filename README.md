
---

Convert an Asana project to RoamResearch page

The development is supported by <a href="https://roam.garden/"> <img src="https://roam.garden/static/logo-2740b191a74245dc48ee30c68d5192aa.svg" height="50" /></a> - a service that allows you to publish your Roam notes as a beautiful static website (digital garden)

## Prerequisites:
1. Python 3.7+
2. Dependencies:`pip install -r requirements.txt`

## Usage
1. Obtain a JSON representation of your Asana project and save it to `<ProjectName>.json`

    ![](export.gif)

    You can also use [the exporter](https://github.com/Stvad/AsanaExport) I wrote to obtain a full snapshot of all your projects from all the workspaces.

2. Run `python roam_asana.py ProjectName.json output.json`

3. Import the resulting JSON file to Roam

## Details

1. Task notes are inserted as a child block
1. Subtask become child blocks
1. Tags and due dates are converted into Roam pages and inserted as a first child block under the respective task block
1. Sections are supported and tasks that are in a section are aggregated under the same block
1. This also supports converting [Asana bracket estimate hack](https://github.com/Stvad/RoamAsana) into Roam attribute
