## Settings

```json
{
  "title": "Document Indexer",
  "description": "Index documents based on their semantic content",
  "type": "object",
  "required": [
    "embeddingTransformer",
    "vectorStore"
  ],
  "properties": {
    "embeddingTransformer": {
      "type": "string",
      "title": "Embeddings",
      "description": "Embeddings to use",
      "enum": [
        "Azure OpenAI"
      ],
      "default": "Azure OpenAI"
    },
    "vectorStore": {
      "type": "string",
      "title": "Vector store",
      "description": "Vector store to use",
      "enum": [
        "Postgres pg_vector"
      ],
      "default": "Postgres pg_vector"
    },
    "overwrite": {
      "type": "boolean",
      "title": "Overwrite existing vectors",
      "default": false,
      "description": "Overwrite existing vectors"
    },
    "useCache": {
      "type": "boolean",
      "title": "Cache and use cached results",
      "default": true,
      "description": "Use cached results"
    }
  }
}
```

Tool settings are defined in `config/json_schema.json` file. This json schema is used to display the user input form in the platform. The tool should collect all the information required for its working here. For example, if the tool requires a username and password to connect to a database, the tool should collect these details in the settings form. The settings form is displayed to the user when the tool is added to the workflow. You might also collect API keys and other sensitive information here. The platform will provide this infomation to the tool through command line arguments to the main tool script when it is called as part of the workflow or during debugging runs.

The json schema should be a valid json schema. You can use [jsonschema.net](https://jsonschema.net/) to generate a json schema from a sample json. The json schema should be saved in `config/json_schema.json` file. The platform's front end takes care of validating the user input against this schema. The  platform's backend will pass the user input to the tool as command line arguments and/or environmental variables.

## Tool icon

The tool icon is defined in `config/icon.svg` file. This svg file is displayed in the platform. The icon should be a
square aspect ratio.
