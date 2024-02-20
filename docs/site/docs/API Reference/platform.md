<!-- markdownlint-disable -->



# <kbd>module</kbd> `platform`


---





## <kbd>class</kbd> `UnstractPlatformBase`
Base class to handle interactions with Unstract's platform service. 



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

> - PLATFORM_SERVICE_API_KEY environment variable is required. 





---



## <kbd>class</kbd> `UnstractPlatform`
Implementation of `UnstractPlatformBase` to interact with platform service. 



**Notes:**

> - PLATFORM_SERVICE_API_KEY environment variable is required. 



### <kbd>method</kbd> `__init__`

```python
__init__(tool: UnstractAbstractTool, platform_host: str, platform_port: str)
```

Constructor of the implementation of `UnstractPlatformBase` 



**Args:**
 
 - <b>`tool`</b> (UnstractAbstractTool):  Instance of UnstractAbstractTool 
 - <b>`platform_host`</b> (str):  Host of platform service 
 - <b>`platform_port`</b> (str):  Port of platform service 




---



### <kbd>method</kbd> `get_platform_details`

```python
get_platform_details() → Optional[dict[str, Any]]
```

Obtains platform details associated with the platform key. 

Currently helps fetch organization ID related to the key. 



**Returns:**
 
 - <b>`Optional[dict[str, Any]]`</b>:  Dictionary containing the platform details 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
