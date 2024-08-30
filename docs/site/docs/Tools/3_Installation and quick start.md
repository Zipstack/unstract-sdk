### Install the SDK from pypi

```bash
pip install unstract-sdk
```

### Using the tool generator

```bash
unstract-tool-gen --help

usage: Unstract tool generator [-h] --command COMMAND [--tool-name TOOL_NAME] [--location LOCATION] [--overwrite OVERWRITE]

Script to generate a new Unstract tool

optional arguments:
  -h, --help            show this help message and exit
  --command COMMAND     Command to execute
  --tool-name TOOL_NAME Tool name
  --location LOCATION   Directory to create the new tool in
  --overwrite OVERWRITE Overwrite existing tool

Unstract SDK
```

To create a new tool, run the following command:

```bash
unstract-tool-gen --command NEW \
--tool-name indexer \
--location ~/Devel/Github/unstract/tools/ \
--overwrite false
```

This will create a new tool in the `~/Devel/Github/unstract/tools/` directory. Replace the directory with yours. The tool will be named `indexer`. 

The tool will be created with the following structure:

<img src="/img/page_content/tool-scaffold.png" width="200px"></img>

- `icon.svg` is the icon which will be displayed in the platform
- `json_schema.json` is the json schema for the tool spec
- `properties.json` is the properties file for the tool
- `main.py` is the main file for the tool. This is where the business logic of the tool will be implemented.
- `requirements.txt` is the requirements file for the tool. This is where the dependencies of the tool will be specified.
- `sample.env` is the sample environment file for the tool. This is where the environment variables for the tool will be specified. Make a copy of this as `.env` and fill in the values for the environment variables.
- `.dockerignore` is the docker ignore file for the tool. This is where the files to be ignored by docker will be specified.
- `Dockerfile` is the docker file for the tool. This is used to build the docker image for the tool.
- `README.md` is the readme file for the tool. This is where the documentation for the tool will be specified.

>The docker related files need not be modified unless you are using a different base image or you need to install additional dependencies. The docker image will be built automatically when the tool is deployed to the platform.
