<!-- markdownlint-disable -->



# <kbd>module</kbd> `tool.mixin`






---



## <kbd>class</kbd> `StaticCommandsMixin`
Mixin class to handle static commands for tools. 




---



### <kbd>method</kbd> `icon`

```python
icon(icon_file: str = 'config/icon.svg') → str
```

Returns the icon of the tool. 



**Args:**
 
 - <b>`icon_file`</b> (str):  The path to the icon file. The default is config/icon.svg. 

**Returns:**
 
 - <b>`str`</b>:  The icon of the tool. 

---



### <kbd>method</kbd> `properties`

```python
properties(properties_file: str = 'config/properties.json') → str
```

Returns the properties of the tool. 



**Args:**
 
 - <b>`properties_file`</b> (str):  The path to the properties file. The default is config/properties.json. 

**Returns:**
 
 - <b>`str`</b>:  The properties of the tool. 

---



### <kbd>method</kbd> `spec`

```python
spec(spec_file: str = 'config/spec.json') → str
```

Returns the JSON schema of the tool. 



**Args:**
 
 - <b>`spec_file`</b> (str):  The path to the JSON schema file. The default is config/spec.json. 

**Returns:**
 
 - <b>`str`</b>:  The JSON schema of the tool. 

---



### <kbd>method</kbd> `variables`

```python
variables(variables_file: str = 'config/runtime_variables.json') → str
```

Returns the JSON schema of the runtime variables. 



**Args:**
 
 - <b>`variables_file`</b> (str):  The path to the JSON schema file. The default is config/runtime_variables.json. 

**Returns:**
 
 - <b>`str`</b>:  The JSON schema for the runtime variables. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
