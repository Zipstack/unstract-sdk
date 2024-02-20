
```json
{
  "display_name": "Document Indexer",
  "function_name": "document_indexer",
  "description": "This tool creates indexes and embeddings for documents.",
  "parameters": [
    {
      "name": "input_file",
      "type": "string",
      "description": "File path of the input file"
    }
  ],
  "versions": [
    "1.0.0"
  ],
  "is_cacheable": false,
  "input_type": "file",
  "output_type": "index",
  "requires": {
    "files": {
      "input": true,
      "output": false
    },
    "databases": {
      "input": false,
      "output": false
    }
  }
}
```

Tools are defined using the `config/properties.json` file. This json file contains standard properties for the tool,
explained below

## `display_name`
The name of the tool as displayed in the platform

## `function_name`
A unique name for the tool. This name is used to identify the tool in the platform. This name should be a valid
python function name. This name is also used to name the docker image for the tool. The docker image name is
`unstract/<function_name>`

## `description`
A short description of the tool. This description is displayed in the platform

## `parameters`
An *array* of json objects. Each json object represents a parameter for the tool. Each parameter object has the
following properties `name`, `type` and `description`. These are the _inputs_ to the tool.

### `parameters[x].name`
Is the name of the parameter. This name is used to identify the parameter in the platform.

### `parameters[x].type`
Is the type of the parameter. This type is used to validate the user input in the platform. The type can be `string`
or `number`.

### `parameters[x].description`
Is a short description of the parameter. This description is displayed in the platform.

## `is_cachable`
A boolean value indicating whether the tool is cachable or not. If the tool is cachable, the platform will allow
caching if the tool is setup to cache.

## `input_type`
The type of input for the tool. This can be `file`, `db` or `index`

## `output_type`
The type of output for the tool. This can be `file`, `db` or `index`

## `required`

### `required.files.input`
A boolean value to indicate whether the tool requires input files or not.

### `required.files.output`
A boolean value to indicate whether the tool produces output files or not.

### `required.db.input`
A boolean value to indicate whether the tool requires input database or not.

### `required.db.output`
A boolean value to indicate whether the tool produces output database or not.
