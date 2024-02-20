<!-- markdownlint-disable -->



# <kbd>module</kbd> `dbs`




**Global Variables**
---------------
- **connectors**


---



## <kbd>class</kbd> `UnstractToolDB`
Class to handle DB connectors for Unstract Tools. 



**Notes:**

> - PLATFORM_SERVICE_API_KEY environment variable is required. 



### <kbd>method</kbd> `__init__`

```python
__init__(
    tool: UnstractAbstractTool,
    platform_host: str,
    platform_port: str
) → None
```



**Args:**
 
 - <b>`tool`</b> (UnstractAbstractTool):  Instance of UnstractAbstractTool 
 - <b>`platform_host`</b> (str):  Host of platform service 
 - <b>`platform_port`</b> (str):  Port of platform service 



**Notes:**

> - PLATFORM_SERVICE_API_KEY environment variable is required. - The platform_host and platform_port are the host and port of the platform service. 




---



### <kbd>method</kbd> `get_engine`

```python
get_engine(tool_instance_id: str) → Any
```

Get DB engine  1. Get the connection settings from platform service  using the tool_instance_id  2. Create UnstractFileSystem based object using the settings  2.1 Find the type of the database (From Connector Registry)  2.2 Create the object using the type  (derived class of UnstractFileSystem)  3. Send Object.get_fsspec_fs() to the caller 



**Args:**
 
 - <b>`tool_instance_id`</b> (str):  tool Instance Id 



**Returns:**
 
 - <b>`Any`</b>:  _description_ 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
