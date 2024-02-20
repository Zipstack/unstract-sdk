<!-- markdownlint-disable -->



# <kbd>module</kbd> `file_system`




**Global Variables**
---------------
- **connectors**


---



## <kbd>class</kbd> `UnstractToolFileSystem`
Class to handle File connectors for Unstract Tools. 



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



### <kbd>method</kbd> `get_fsspec`

```python
get_fsspec(
    tool_instance_id: str,
    connector_type: str = 'OUTPUT'
) → Optional[AbstractFileSystem]
```

Get FsSpec for fileSystem  1. Get the connection settings from platform service  using the tool_instance_id  2. Create UnstractFileSystem based object using the settings  2.1 Find the type of the database (From Connector Registry)  2.2 Create the object using the type  (derived class of UnstractFileSystem)  3. Send Object.get_fsspec_fs() to the caller 



**Args:**
 
 - <b>`tool_instance_id`</b> (str):  tool Instance Id 
 - <b>`connector_type`</b> (str, optional):  _description_.  Defaults to ConnectorType.OUTPUT. 



**Returns:**
 
 - <b>`Any`</b>:  _description_ 

---



### <kbd>method</kbd> `get_fsspec_fs`

```python
get_fsspec_fs(
    tool: UnstractAbstractTool,
    tool_instance_id: str,
    fileType: str
) → AbstractFileSystem
```

Get fileSystem spec by the help of unstract DB tool. 



**Args:**
 
 - <b>`tool_instance_id`</b> (str):  ID of the tool instance 
 - <b>`fileType`</b> (str):  INPUT/OUTPUT 
 - <b>`tool`</b> (UnstractAbstractTool):  Instance of UnstractAbstractTool Required env variables: 
 - <b>`PLATFORM_HOST`</b>:  Host of platform service 
 - <b>`PLATFORM_PORT`</b>:  Port of platform service 

**Returns:**
 
 - <b>`Any`</b>:  engine 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
