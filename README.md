<div align="center">
<img src="https://raw.githubusercontent.com/Zipstack/unstract-sdk/main/docs/assets/unstract_u_logo.png" style="height: 120px">

# Unstract

## No-code LLM Platform to launch APIs and ETL Pipelines to structure unstructured documents

</div>

# Unstract SDK

The `unstract-sdk` package helps with developing tools that are meant to be run on the Unstract platform. This includes
modules to help with tool development and execution, caching, making calls to LLMs / vectorDBs / embeddings .etc.
They also contain helper methods/classes to aid with other tasks such as indexing and auditing the LLM calls.

## Installation

- The below libraries need to be installed to run the SDK
  - Linux

    ```
    sudo apt install build-essential pkg-config libmagic-dev tesseract-ocr pandoc
    ```

  - Mac

    ```
    brew install pkg-config libmagic pandoc tesseract-ocr
    ```

## Tools

### Create a scaffolding for a new tool

Example

```bash
unstract-tool-gen --command NEW --tool-name <name of tool> \
 --location ~/path_to_repository/unstract-tools/ --overwrite false
```

Supported commands:

- `NEW` - Create a new tool

### Environment variables required for all Tools

| Variable                   | Description                                                           |
| -------------------------- | --------------------------------------------------------------------- |
| `PLATFORM_SERVICE_HOST`    | The host in which the platform service is running                     |
| `PLATFORM_SERVICE_PORT`    | The port in which the service is listening                            |
| `PLATFORM_SERVICE_API_KEY` | The API key for the platform                                          |
| `TOOL_DATA_DIR`            | The directory in the filesystem which has contents for tool execution |

### Llama Index support

Unstract SDK 0.3.2 uses the following version of Llama
Index Version **0.9.28** as on January 14th, 2024

### Developing with the SDK

Ensure that you have all the required dependencies and pre-commit hooks installed
```shell
pdm install
pre-commit install
```

Once the changes have been made, it can be tested with [Unstract](https://github.com/Zipstack/unstract) through the following means.

#### With PDM
Specify the SDK as a dependency to a project using a tool like `pdm` by adding the following to your `pyproject.toml`

```toml
[tool.pdm.dev-dependencies]
local_copies = [
    "-e unstract-adapters @ file:///${UNSTRACT_ADAPTERS_PATH}",
    "-e unstract-sdk @ file:///${UNSTRACT_SDK_PATH}",
]
```
Or by running the below command
```shell
pdm add -e /path/to/unstract-sdk --dev
```

#### With pip
- If the project is using `pip` it might be possible to add it as a dependency in `requirements.txt`
```
-e /path/to/unstract-sdk
```
NOTE: Building locally might require the below section to be replaced in the `unstract-sdk`'s build system configuration
```
[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"
```
- Another option is to provide a git URL in `requirements.txt`, this can come in handy while building tool
docker images. Don't forget to run `apt install git` within the `Dockerfile` for this
```shell
unstract-sdk @ git+https://github.com/Zipstack/unstract-sdk@feature-branch
```

- Or try installing a [local PyPI server](https://pypi.org/project/pypiserver/) and upload / download your package from this server


### Documentation generation

Follow [this README.md](https://github.com/Zipstack/unstract-sdk/blob/main/docs/README.md) for generating documentation.
