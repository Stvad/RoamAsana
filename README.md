Converts

## Prerequisites:
1. Python 3.7+
2. Dependencies:`pip install -r requirements.txt`

## Usage
1. Obtain a JSON representation of your Asana project and save it to `<ProjectName>.json`

    ![](export.gif)

    You can also use [the exporter](https://github.com/Stvad/AsanaExport) I wrote to obtain a full snapshot of all your projects from all the workspaces.

2. Run `python roam_asana.py ProjectName.json output.json`

3. Import the resulting JSON file to Roam