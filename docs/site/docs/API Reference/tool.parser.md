<!-- markdownlint-disable -->



# <kbd>module</kbd> `tool.parser`






---



## <kbd>class</kbd> `ToolArgsParser`
Class to help with parsing arguments to a tool. 




---



### <kbd>classmethod</kbd> `get_log_level`

```python
get_log_level(args: list) → Optional[str]
```

Returns the log level for a tool. 

If its not present in the parsed arguments, `None` is returned. 



**Args:**
 
 - <b>`args`</b> (List[str]):  Command line arguments received by a tool 



**Returns:**
 
 - <b>`Optional[str]`</b>:  Log level of either INFO, DEBUG, WARN, ERROR, FATAL if  present in the args. Otherwise returns `None`. 

---



### <kbd>method</kbd> `parse_args`

```python
parse_args(args_to_parse: list) → Namespace
```

Helps parse arguments to a tool. 



**Args:**
 
 - <b>`args_to_parse`</b> (List[str]):  Command line arguments received by a tool 



**Returns:**
 
 - <b>`argparse.Namespace`</b>:  Parsed arguments 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
