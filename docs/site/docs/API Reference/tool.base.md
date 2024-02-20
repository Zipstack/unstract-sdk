<!-- markdownlint-disable -->



# <kbd>module</kbd> `tool.base`






---



## <kbd>class</kbd> `UnstractAbstractTool`
Abstract class for Unstract tools. 



### <kbd>method</kbd> `__init__`

```python
__init__(log_level: str = <LogLevel.INFO: 'INFO'>) → None
```

Creates an UnstractTool. 



**Args:**
 
 - <b>`log_level`</b> (str):  Log level for the tool  Can be one of INFO, DEBUG, WARN, ERROR, FATAL. 




---



### <kbd>method</kbd> `elapsed_time`

```python
elapsed_time() → float
```

Returns the elapsed time since the tool was created. 

---



### <kbd>classmethod</kbd> `from_tool_args`

```python
from_tool_args(args: list) → UnstractAbstractTool
```

Builder method to create a tool from args passed to a tool. 

Refer the tool's README to know more about the possible args 



**Args:**
 
 - <b>`args`</b> (List[str]):  Arguments passed to a tool 



**Returns:**
 
 - <b>`UnstractAbstractTool`</b>:  Abstract base tool class 

---



### <kbd>method</kbd> `run`

```python
run(params: dict, settings: dict, workflow_id: str) → None
```

Implements RUN command for the tool. 



**Args:**
 
 - <b>`params`</b> (dict[str, Any]):  Params for the tool 
 - <b>`settings`</b> (dict[str, Any]):  Settings for the tool 
 - <b>`workflow_id`</b> (str):  Project GUID used during workflow execution 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
