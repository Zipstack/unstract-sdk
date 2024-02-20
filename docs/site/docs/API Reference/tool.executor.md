<!-- markdownlint-disable -->



# <kbd>module</kbd> `tool.executor`






---



## <kbd>class</kbd> `ToolExecutor`
Takes care of executing a tool's intended command. 



### <kbd>method</kbd> `__init__`

```python
__init__(tool: UnstractAbstractTool) → None
```








---



### <kbd>method</kbd> `execute`

```python
execute(args: Namespace) → None
```

Executes the tool with the passed arguments. 



**Args:**
 
 - <b>`args`</b> (argparse.Namespace):  Parsed arguments to execute with 

---



### <kbd>method</kbd> `load_environment`

```python
load_environment(path: Optional[str] = None)
```

Loads env variables with python-dotenv. 



**Args:**
 
 - <b>`path`</b> (Optional[str], optional):  Path to the env file to load.  Defaults to None. 

---



### <kbd>method</kbd> `validate_and_get_params`

```python
validate_and_get_params(args: Namespace) → dict[str, Any]
```

Validates and obtains params for a tool. 

Validation is done against the tool's params based on its declared PROPERTIES 



**Args:**
 
 - <b>`args`</b> (argparse.Namespace):  Parsed arguments for a tool 



**Returns:**
 
 - <b>`dict[str, Any]`</b>:  Params JSON for a tool 

---



### <kbd>method</kbd> `validate_and_get_settings`

```python
validate_and_get_settings(args: Namespace) → dict[str, Any]
```

Validates and obtains settings for a tool. 

Validation is done against the tool's settings based on its declared SPEC 



**Args:**
 
 - <b>`args`</b> (argparse.Namespace):  Parsed arguments for a tool 



**Returns:**
 
 - <b>`dict[str, Any]`</b>:  Settings JSON for a tool 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
