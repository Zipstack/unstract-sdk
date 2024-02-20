<!-- markdownlint-disable -->


# <kbd>module</kbd> `cache`






---


## <kbd>class</kbd> `UnstractToolCache`
Class to handle caching for Unstract Tools. 



**Notes:**

> - PLATFORM_SERVICE_API_KEY environment variable is required. 


### <kbd>method</kbd> `__init__`

```python
__init__(
    tool: UnstractAbstractTool,
    platform_host: str,
    platform_port: int
) → None
```



**Args:**
 
 - <b>`tool`</b> (UnstractAbstractTool):  Instance of UnstractAbstractTool 
 - <b>`platform_host`</b> (str):  The host of the platform. 
 - <b>`platform_port`</b> (int):  The port of the platform. 



**Notes:**

> - PLATFORM_SERVICE_API_KEY environment variable is required. - The platform_host and platform_port are the host and port of the platform service. 




---


### <kbd>method</kbd> `delete`

```python
delete(key: str) → bool
```

Deletes the value for a key in the cache. 



**Args:**
 
 - <b>`key`</b> (str):  The key. 



**Returns:**
 
 - <b>`bool`</b>:  Whether the operation was successful. 

---


### <kbd>method</kbd> `get`

```python
get(key: str) → Optional[Any]
```

Gets the value for a key in the cache. 



**Args:**
 
 - <b>`key`</b> (str):  The key. 



**Returns:**
 
 - <b>`str`</b>:  The value. 

---


### <kbd>method</kbd> `set`

```python
set(key: str, value: str) → bool
```

Sets the value for a key in the cache. 



**Args:**
 
 - <b>`key`</b> (str):  The key. 
 - <b>`value`</b> (str):  The value. 



**Returns:**
 
 - <b>`bool`</b>:  Whether the operation was successful. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
