<div align="center">
<img src="docs/assets/unstract_u_logo.png" style="height: 120px">

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

### Environment variables required for various LLMs (deprecated)

- Azure OpenAI
  - `OPENAI_API_KEY`
  - `OPENAI_API_BASE`
  - `OPENAI_API_VERSION`
  - `OPENAI_API_ENGINE`
  - `OPENAI_API_MODEL`

### Documentation generation

Follow [this README.md](docs/README.md) for generating documentation.
