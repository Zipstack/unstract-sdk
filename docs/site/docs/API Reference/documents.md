<!-- markdownlint-disable -->



# <kbd>module</kbd> `documents`






---



## <kbd>class</kbd> `UnstractToolDocs`
Class to handle documents for Unstract Tools. 



**Notes:**

> - PLATFORM_SERVICE_API_KEY environment variable is required. 



### <kbd>method</kbd> `__init__`

```python
__init__(tool: UnstractAbstractTool, platform_host: str, platform_port: int)
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
delete(project_id: str, unique_file_id: str)
```

Deletes data for a document from the platform. 



**Notes:**

> - This method is used internally. Do not call this method directly unless you know what you are doing. 
>

**Args:**
 
 - <b>`project_id`</b> (str):  The project id. 
 - <b>`unique_file_id`</b> (str):  The unique file id. 



**Returns:**
 
 - <b>`bool`</b>:  Whether the operation was successful. 

---



### <kbd>method</kbd> `get`

```python
get(project_id: str, unique_file_id: str) → Optional[dict]
```

Retrieves data for a document from the platform. 



**Args:**
 
 - <b>`project_id`</b> (str):  The project id. 
 - <b>`unique_file_id`</b> (str):  The unique file id. 



**Returns:**
 
 - <b>`Optional[dict]`</b>:  The data for the document. 

---



### <kbd>method</kbd> `index_file`

```python
index_file(
    project_id: str,
    embedding_type: str,
    vector_db: str,
    file_path: str,
    overwrite: bool = False
) → dict
```

Indexes a file to the platform. 



**Args:**
 
 - <b>`project_id`</b> (str):  The project id. 
 - <b>`embedding_type`</b> (str):  The embedding type.  Supported values: 
            - "Azure OpenAI" 
 - <b>`vector_db`</b> (str):  The vector db.  Supported values: 
            - "Postgres pg_vector" 
 - <b>`file_path`</b> (str):  The path to the file to index. 
 - <b>`overwrite`</b> (bool):  Whether to overwrite the file if it already exists.  The default is False. 



**Returns:**
 
 - <b>`dict`</b>:  The result of the indexing operation. 



**Notes:**

> Sample return dict: { "status": "OK", "error": "", "cost": 746, "unique_file_id": "9b44826ff1ed4dfd5dda762776acd4dd" } 

---



### <kbd>method</kbd> `insert`

```python
insert(
    project_id: str,
    unique_file_id: str,
    filename: str,
    filetype: str,
    summary: str,
    embedding_tokens: int,
    llm_tokens: int,
    vector_db: str
)
```

Inserts data for a document into the platform. 



**Notes:**

> - This method is typically called by the tool's index() method. It is not typically called directly. 
>

**Args:**
 
 - <b>`project_id`</b> (str):  The project id. 
 - <b>`unique_file_id`</b> (str):  The unique file id. 
 - <b>`filename`</b> (str):  The filename. 
 - <b>`filetype`</b> (str):  The filetype. Example: "application/pdf" 
 - <b>`summary`</b> (str):  The summary. Note: Currently not used. 
 - <b>`embedding_tokens`</b> (int):  The number of tokens used for the embedding. 
 - <b>`llm_tokens`</b> (int):  The number of tokens used for the LLM. 
 - <b>`vector_db`</b> (str):  The vector db.  Supported values: 
            - "Postgres pg_vector" 



**Returns:**
 
 - <b>`bool`</b>:  Whether the operation was successful. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
