<!-- markdownlint-disable -->



# <kbd>module</kbd> `tool.stream`






---



## <kbd>class</kbd> `StreamableBaseTool`
Helper class for streaming Unstract tool commands. 

A utility class to make writing Unstract tools easier. It provides methods to stream the JSON schema, properties, icon, log messages, cost, single step messages, and results using the Unstract protocol to stdout. 



### <kbd>method</kbd> `__init__`

```python
__init__(log_level: LogLevel = <LogLevel.INFO: 'INFO'>) → None
```



**Args:**
 
 - <b>`log_level`</b> (LogLevel):  The log level for filtering of log messages. The default is INFO.  Allowed values are DEBUG, INFO, WARN, ERROR, and FATAL. 




---



### <kbd>method</kbd> `get_env_or_die`

```python
get_env_or_die(env_key: str) → str
```

Returns the value of an env variable. 

If its empty or None, raises an error and exits 



**Args:**
 
 - <b>`env_key`</b> (str):  Key to retrieve 



**Returns:**
 
 - <b>`str`</b>:  Value of the env 

---



### <kbd>method</kbd> `handle_static_command`

```python
handle_static_command(command: str) → None
```

Handles a static command. 

Used to handle commands that do not require any processing. Currently, the only supported static commands are SPEC, PROPERTIES, VARIABLES and ICON. 

This is used by the Unstract SDK to handle static commands. It is not intended to be used by the tool. The tool stub will automatically handle static commands. 



**Args:**
 
 - <b>`command`</b> (str):  The static command. 

**Returns:**
 None 

---



### <kbd>method</kbd> `stream_cost`

```python
stream_cost(cost: float, cost_units: str, **kwargs) → None
```

Streams the cost of the tool using the Unstract protocol COST to stdout. 



**Args:**
 
 - <b>`cost`</b> (float):  The cost of the tool. 
 - <b>`cost_units`</b> (str):  The cost units of the tool. 
 - <b>`**kwargs`</b>:  Additional keyword arguments to include in the record. 

**Returns:**
 None 

---



### <kbd>method</kbd> `stream_error_and_exit`

```python
stream_error_and_exit(message: str) → None
```

Stream error log and exit. 



**Args:**
 
 - <b>`message`</b> (str):  Error message 

---



### <kbd>method</kbd> `stream_icon`

```python
stream_icon(icon: str) → None
```

Streams the icon of the tool using the Unstract protocol ICON to stdout. 



**Args:**
 
 - <b>`icon`</b> (str):  The icon of the tool. Typically returned by the icon() method. 

**Returns:**
 None 

---



### <kbd>method</kbd> `stream_log`

```python
stream_log(
    log: str,
    level: LogLevel = <LogLevel.INFO: 'INFO'>,
    stage: str = 'TOOL_RUN',
    **kwargs
) → None
```

Streams a log message using the Unstract protocol LOG to stdout. 



**Args:**
 
 - <b>`log`</b> (str):  The log message. 
 - <b>`level`</b> (LogLevel):  The log level. The default is INFO.  Allowed values are DEBUG, INFO, WARN, ERROR, and FATAL. 
 - <b>`stage`</b> (str):  LogStage from constant default Tool_RUN 

**Returns:**
 None 

---



### <kbd>method</kbd> `stream_properties`

```python
stream_properties(properties: str) → None
```

Streams the properties of the tool using the Unstract protocol PROPERTIES to stdout. 



**Args:**
 
 - <b>`properties`</b> (str):  The properties of the tool. Typically returned by the properties() method. 

**Returns:**
 None 

---



### <kbd>method</kbd> `stream_result`

```python
stream_result(result: dict, **kwargs) → None
```

Streams the result of the tool using the Unstract protocol RESULT to stdout. 



**Args:**
 
 - <b>`result`</b> (dict):  The result of the tool. Refer to the Unstract protocol for the format of the result. 
 - <b>`**kwargs`</b>:  Additional keyword arguments to include in the record. 

**Returns:**
 None 

---



### <kbd>method</kbd> `stream_single_step_message`

```python
stream_single_step_message(message: str, **kwargs) → None
```

Streams a single step message using the Unstract protocol SINGLE_STEP_MESSAGE to stdout. 



**Args:**
 
 - <b>`message`</b> (str):  The single step message. 
 - <b>`**kwargs`</b>:  Additional keyword arguments to include in the record. 

**Returns:**
 None 

---



### <kbd>method</kbd> `stream_spec`

```python
stream_spec(spec: str) → None
```

Streams JSON schema of the tool using the Unstract protocol SPEC to stdout. 



**Args:**
 
 - <b>`spec`</b> (str):  The JSON schema of the tool. Typically returned by the spec() method. 



**Returns:**
 None 

---



### <kbd>method</kbd> `stream_update`

```python
stream_update(message: str, component: str, state: str, **kwargs) → None
```

Streams a log message using the Unstract protocol UPDATE to stdout. 



**Args:**
 
 - <b>`message`</b> (str):  The log message. 
 - <b>`component`</b> (str):  Component to update 
 - <b>`state`</b> (str):  LogState from constant 

---



### <kbd>method</kbd> `stream_variables`

```python
stream_variables(variables: str) → None
```

Streams JSON schema of the tool's variables using the Unstract protocol VARIABLES to stdout. 



**Args:**
 
 - <b>`variables`</b> (str):  The tool's runtime variables. Typically returned by the spec() method. 



**Returns:**
 None 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
