<!-- markdownlint-disable -->



# <kbd>module</kbd> `llm`






---



## <kbd>class</kbd> `UnstractToolLLM`
Class to handle LLMs for Unstract Tools. 



### <kbd>method</kbd> `__init__`

```python
__init__(tool: UnstractAbstractTool, llm_id: str)
```



**Notes:**

> - "Azure OpenAI" : Environment variables required OPENAI_API_KEY, OPENAI_API_BASE, OPENAI_API_VERSION, OPENAI_API_ENGINE, OPENAI_API_MODEL 
>

**Args:**
 
 - <b>`tool`</b> (UnstractAbstractTool):  Instance of UnstractAbstractTool 
 - <b>`llm_id`</b> (str):  The id of the LLM to use.  Supported values: 
            - "Azure OpenAI" 




---



### <kbd>method</kbd> `get_callback_manager`

```python
get_callback_manager() → Optional[CallbackManager]
```

Returns the Callback Manager object for the tool. 



**Returns:**
 
 - <b>`Optional[CallbackManager]`</b>:  The Callback Manager object for the tool.  (llama_index.callbacks.CallbackManager) 

---



### <kbd>method</kbd> `get_llm`

```python
get_llm() → Optional[LLM]
```

Returns the LLM object for the tool. 



**Returns:**
 
 - <b>`Optional[LLM]`</b>:  The LLM object for the tool. (llama_index.llms.base.LLM) 

---



### <kbd>method</kbd> `get_max_tokens`

```python
get_max_tokens(reserved_for_output: int = 0) → int
```

Returns the maximum number of tokens that can be used for the LLM. 



**Args:**
 
 - <b>`reserved_for_output`</b> (int):  The number of tokens reserved for the output.  The default is 0. 



**Returns:**
 
 - <b>`int`</b>:  The maximum number of tokens that can be used for the LLM. 

---



### <kbd>method</kbd> `get_usage_counts`

```python
get_usage_counts() → dict[str, int]
```

Returns the usage counts for the tool. 



**Returns:**
 
 - <b>`dict`</b>:  The usage counts for the tool. 
        - embedding_tokens: The number of tokens used for the embedding. 
        - llm_prompt_tokens: The number of tokens used for the LLM prompt. 
        - llm_completion_tokens:  The number of tokens used for the LLM completion. 
        - total_llm_tokens: The total number of tokens used for the LLM. 

---



### <kbd>method</kbd> `reset_usage_counts`

```python
reset_usage_counts() → None
```

Resets the usage counts for the tool. 



**Returns:**
  None 

---



### <kbd>method</kbd> `stream_usage_counts`

```python
stream_usage_counts() → None
```

Stream all usage costs. 

This function retrieves the usage counts and stream the costs associated with it. 



**Returns:**
  None 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
