Unstract platform tools can we written in any language as long as they communicate with the platform using the protocol described below. The **Python SDK** provides a convenient interface to the platform to create your own tools. **The SDK abstracts away the details of the protocol and provides a convenient interface to the platform to create your own tools**.


The protocol is based on simple text messages encapsulated in JSON.

List of message types:

- `SPEC`
- `PROPERTIES`
- `ICON`
- `LOG`
- `COST`
- `RESULT`
- `SINGLE_STEP_MESSAGE`

Message type details:

## `SPEC` message

```json
{
  "type": "SPEC",
  "spec": "<SPEC JSON>",
  "emitted_at": "<TIMESTAMP IN ISO FORMAT>"
}
``` 

The `spec` property contains the json from `json_schema.json`. Refer to tool spec documentation for more details.

## `PROPERTIES` message

```json
{
  "type": "PROPERTIES",
  "properties": "<PROPERTIES JSON>",
  "emitted_at": "<TIMESTAMP IN ISO FORMAT>"
} 
```

The `properties` property contains the json from `properties.json`. Refer to tool definition section for more information

## `ICON` message

```json
{
  "type": "ICON",
  "icon": "<ICON SVG>",
  "emitted_at": "<TIMESTAMP IN ISO FORMAT>"
} 
```

The `icon` property contains the svg from `icon.svg`. Refer to *tool icon* section for more details. Note that this is
returns the SVG text itself and not the path to the SVG file.

## `LOG` message

```json
{
  "type": "LOG",
  "level": "<LOG LEVEL>",
  "log": "<LOG MESSAGE>",
  "emitted_at": "<TIMESTAMP IN ISO FORMAT>"
} 
```

The `log` property contains a log message. The level property can contain one
of `DEBUG`, `INFO`, `WARN`, `ERROR`, `FATAL`

## `COST` message

```json
{
  "type": "COST",
  "cost": "<COST>",
  "cost_units": "<COST UNITS>",
  "emitted_at": "<TIMESTAMP IN ISO FORMAT>"
} 
```

The `cost` property contains the cost of the tool run. The `cost` is a floating point number and `cost_units` is a
string

## `RESULT` message

```json
{
  "type": "RESULT",
  "result": {
    "workflow_id": "<WORKFLOW_ID>",
    "elapsed_time": "<ELAPSED TIME>",
    "output": "<OUTPUT JSON or STRING>"
  },
  "emitted_at": "<TIMESTAMP IN ISO FORMAT>"
} 
```

The `result` property contains the result of the tool run. The `result` is a json object. The `result` json object has a
standard format mentioned above.

## `SINGLE_STEP_MESSAGE` message

```json
{
  "type": "SINGLE_STEP_MESSAGE",
  "message": "<MESSAGE>",
  "emitted_at": "<TIMESTAMP IN ISO FORMAT>"
} 
```

The `message` property contains a message to be displayed to the user. This message is displayed in the platform IDE during
single stepping (debug mode). T
