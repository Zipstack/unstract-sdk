In most cases, implementing the tool involves writing your business logic in the `run` function in the `main.py` file. All other logic to setup the toll and provide metadata is already implemented in the code generated by the SDK.

Let's walk through a sample code for a **classifier** tool

>Note that this is not a production ready implementation. Just an informal introduction to the tool implementation

### Tool properties
```json
{
  "display_name": "File Classifier",
  "function_name": "classify",
  "description": "Classifies a file or folder based on its contents",
  "parameters": [
    {
      "name": "input_file",
      "type": "string",
      "description": "The file operation which needs to be performed"
    }
  ],
  "versions": [
    "1.0.0"
  ],
  "is_cacheable": true,
  "input_type": "file",
  "output_type": "file",
  "requires": {
    "files": {
      "input": true,
      "output": true
    },
    "databases": {
      "input": false,
      "output": false
    }
  }
}
```

### Tool settings (JSON Schema)
```json
{
  "title": "Document classifier",
  "description": "Classify documents based on their content",
  "type": "object",
  "required": [
  ],
  "properties": {
    "classifier": {
      "type": "string",
      "title": "Classifier",
      "description": "Classifier to use",
      "enum": [
        "Azure OpenAI"
      ],
      "default": "Azure OpenAI"
    },
    "classificationBins": {
      "type": "array",
      "title": "Classification bins",
      "description": "Classification bins",
      "items": {
        "type": "string"
      }
    },
    "action": {
      "type": "string",
      "title": "Action",
      "description": "Action to perform",
      "enum": [
        "Copy",
        "Move"
      ],
      "default": "Copy"
    },
    "outputFolder": {
      "type": "string",
      "title": "Output folder",
      "default": "output",
      "description": "Folder to store the output"
    },
    "useCache": {
      "type": "boolean",
      "title": "Cache and use cached results",
      "default": true,
      "description": "Use cached results"
    }
  }
}
```

### Sample implementation


```python
def run(
    params: dict[str, Any],
    settings: dict[str, Any],
    workflow_id: str,
    utils: UnstractToolUtils,
) -> None:
```

- `params` dictionary will contain the output of the previous stage
- `settings` dictionary will contain the settings configured for the tool
- `workflow_id` is the guid of the project
- `utils` is an instantiated class of `UnstractToolUtils`. Refer to the API reference for more information

```python
    MOUNTED_FSSPEC_DIR_INPUT = "/mnt/unstract/fs_input/"
    MOUNTED_FSSPEC_DIR_OUTPUT = "/mnt/unstract/fs_output/"
```
These directories are automatically mounted with the file connector. For local testing, you can change these to your local directories

```python

    input_file = params["input_file"]
    output_folder = settings["outputFolder"]
    classifier = settings["classifier"]
    bins = settings["classificationBins"]
    action = settings["action"]
    use_cache = settings["useCache"]
```

The keys for the dictionaries are the same names in the properties and json schema for the tools (Refer to the tool properties and settings sections above). Whatever user specifies in the tool settings in the frontend will be provided through the settings dictionary

```python

    if len(bins) < 2:
        utils.stream_log("At least two bins are required", "ERROR")
        exit(1)

    allowed_classifiers = ["Azure OpenAI"]
    if classifier not in allowed_classifiers:
        utils.stream_log(
            f"Invalid classifier. Only {allowed_classifiers} are allowed", "ERROR"
        )
        exit(1)

    if input_file.startswith("/"):
        input_file = input_file[1:]
    input_file = f"{MOUNTED_FSSPEC_DIR_INPUT}{input_file}"

    if output_folder.startswith("/"):
        output_folder = output_folder[1:]
    output_folder = f"{MOUNTED_FSSPEC_DIR_OUTPUT}{output_folder}"

    if not os.path.isfile(input_file):
        utils.stream_log(f"Input file not found: {input_file}", "ERROR")
        exit(1)

    utils.stream_log(f"Input file: {input_file}")
    utils.stream_log(f"Output folder: {output_folder}")

```
Note the use of logging helper function `utils.stream_log()` to log information. This helper function creates Unstract protocol messages which will be captured by the platform and used downstream. Refer to the API reference for more information on how to use the utility functions

```python

    # All validations are done. Now run the function
    input_file_type = None
    input_file_type_mime = None
    with open(input_file, mode="rb") as input_file_obj:
        sample_contents = input_file_obj.read(100)
        input_file_type = filetype.guess(sample_contents)

    if input_file_type is None:
        input_file_type_mime = "text/plain"
    else:
        input_file_type_mime = input_file_type.MIME

    utils.stream_log(f"Input file type: {input_file_type_mime}")

    utils.stream_log("Partitioning file...")
    try:
        elements = partition(filename=input_file)
    except Exception as e:
        utils.stream_log(f"Error partitioning file: {e}", "ERROR")
        exit(1)
    text = "\n\n".join([str(el) for el in elements])

    utils.stream_log(f"Text length: {len(text)}")

```

Files are handled in a pythonic way. Also note the use of two modules `unstructerd.io` (partitioning) and `filetype` which are specific to this tool. These modules should be included in the tool's `requirements.txt`

```python

    input_text_for_log = text
    if len(input_text_for_log) > 500:
        input_text_for_log = input_text_for_log[:500] + "...(truncated)"
    utils.stream_single_step_message(
        f"### Input text\n\n```text\n{input_text_for_log}\n```\n\n"
    )

```

Another utility function is used here. `utils.stream_single_step_message()`. This function is used to display messages to the user during single stepping (debugging) mode. This is useful to display the input and output of the tool to the user during debugging. Refer to the API reference for more information.


```python

    if "unknown" not in bins:
        bins.append("unknown")
    bins_with_quotes = [f"'{b}'" for b in bins]

    tool_llm = UnstractToolLLM(utils=utils, llm_id=classifier)
    llm = tool_llm.get_llm()
    cb = tool_llm.get_callback_manager()
    service_context = ServiceContext.from_defaults(
        llm=llm, callback_manager=cb)
    set_global_service_context(service_context)

    max_tokens = tool_llm.get_max_tokens(reserved_for_output=50 + 1000)
    max_bytes = int(max_tokens * 1.3)
    utils.stream_log(
        f"LLM Max tokens: {max_tokens} ==> Max bytes: {max_bytes}")
    limited_text = ""
    for byte in text.encode():
        if len(limited_text.encode()) < max_bytes:
            limited_text += chr(byte)
        else:
            break
    text = limited_text
    utils.stream_log(f"Lenght of text: {len(text.encode())} {len(text)}")
```

The SDK's LLM module is used in the code above. The LLM module is used to interact with the LLMs configured in the platform. The LLM module abstracts away the complexities of the underlying LLMs and provides a simple interface to interact with the LLMs. Refer to the API reference for more information on how to use the LLM module. This SDK module returns a Llamaindex LLM object. Refer to the Llamaindex documentation for more details on how the object can be used.


```python
    prompt = (
        f"Classify the following text into one of the following categories: {' '.join(bins_with_quotes)}.\n\n"  # noqa: E501
        f"Your categorisation should be strictly exactly one of the items in the "
        f"categories given. Find a semantic match of category if possible. If it does not categorise well "  # noqa: E501
        f"into any of the listed categories, categorise it as 'unknown'.\n\nText:\n\n{text}\n\n\nCategory:"  # noqa: E501
    )

    prompt_hash = (
        f"cache:{workflow_id}:{classifier}:{hashlib.md5(prompt.encode()).hexdigest()}"
    )

    classification = None
    if use_cache:
        cache = UnstractToolCache(
            utils=utils,
            platform_host=utils.get_env_or_die("PLATFORM_HOST"),
            platform_port=int(utils.get_env_or_die("PLATFORM_PORT")),
        )
        cached_response = cache.get(prompt_hash)
        if cached_response is not None:
            classification = cached_response
            utils.stream_cost(cost=0.0, cost_units="cache")

    if classification is None:
        utils.stream_log("Calling LLM")
        try:
            response = llm.complete(prompt, max_tokens=50, stop=["\n"])
            tool_llm.stream_usage_counts()
            if response is None:
                utils.stream_log("Error calling LLM", "ERROR")
                exit(1)
            classification = response.text.strip()
            utils.stream_log(f"LLM response: {response}")
        except Exception as e:
            utils.stream_log(f"Error calling LLM: {e}", "ERROR")
            exit(1)

        if use_cache:
            cache = UnstractToolCache(
                utils=utils,
                platform_host=utils.get_env_or_die("PLATFORM_HOST"),
                platform_port=int(utils.get_env_or_die("PLATFORM_PORT")),
            )
            cache.set(prompt_hash, classification)
```
In the code above, caching module provided by the SDK is used. The results from the LLMs can be cached for better performance and cost saving. Refer to the API reference for more information

```python

    classification = classification.lower()
    bins = [bin.lower() for bin in bins]

    if classification not in bins:
        utils.stream_log(
            f"Invalid classification done: {classification}", "ERROR")
        exit(1)

    try:
        output_folder_bin = os.path.join(output_folder, classification)
        if not os.path.exists(output_folder_bin):
            os.makedirs(output_folder_bin, exist_ok=True)

        output_file_bin = f"{output_folder_bin}/{os.path.basename(input_file)}"
        with open(input_file, "rb") as file_in:
            with open(output_file_bin, "wb") as file_out:
                file_out.write(file_in.read())
    except Exception as e:
        utils.stream_log(f"Error creating output file: {e}", "ERROR")
        exit(1)

    if action.lower() == "move":
        try:
            os.remove(input_file)
        except Exception as e:
            utils.stream_log(f"Error deleting input file: {e}", "ERROR")
            exit(1)

    output_log = "### Classier output\n\n"
    output_log += f"```bash\nCLASSIFICATION={classification}\n```\n\n"
    utils.stream_single_step_message(output_log)

    result = {
        "workflow_id": workflow_id,
        "elapsed_time": utils.elapsed_time(),
        "output": classification,
    }
    utils.stream_result(result)
    return
```

Finally the result is streamed back to the platform using the `utils.stream_result()` function. 

## Testing the tool

### Required environment variables

| Variable           | Description                                       |
| ------------------ | ------------------------------------------------- |
| `PLATFORM_HOST`    | The host in which the platform service is running |
| `PLATFORM_PORT`    | The port in which the service is listening        |
| `PLATFORM_API_KEY` | The API key for the platform                      |

### Testing the tool locally

Setup a virtual environment and install the requirements:

```commandline
python -m venv venv
```

Once a virtual environment is created or if you already have created one, activate it:

```commandline
source venv/bin/activate
```

Install the requirements:

> If you want to use the local sdk (not the one from PyPi), make sure you comment out the `unstract-sdk` line in the `requirements.txt` file.

```commandline
pip install -r requirements.txt
```

To use the local development version of the _unstract sdk_ install it from the local repository. Replace the path with
the path to your local repository:

```commandline
pip install ~/Devel/Github/pandora/sdks/.
```

Load the environment variables:

Make a copy of the `sample.env` file and name it `.env`. Fill in the required values.

```commandline
source .env
```

#### Run SPEC command

To get the tool's spec, run the following command:
```commandline
python main.py --command SPEC
```

#### Run PROPERTIES command

To get the tool's properties, run the following command:
```commandline
python main.py --command PROPERTIES
```

#### Run ICON command

To get the tool's icon, run the following command:
```commandline
python main.py --command ICON
```

#### Run RUN command to classify a document

The format of the jsons required for settings and params can be found by running the SPEC command and the PROPERTIES
command respectively. Alternatively if you have access to the code base, it is located in the `config` folder
as `json_schema.json` and `properties.json`.

> Notes on file locations:
>
> The `input_file` parameter is relative to the `/mnt/unstract/fs_input/` directory. So in the following example the
> file being classified is located at `/mnt/unstract/fs_input/files/bbc-pol-004.txt`. This location can be changed by
> changing the `FILES_PATH` environment variable in the platform service and not in the classifier tool.

```commandline
python main.py \
    --command RUN \
    --params '{
        "input_file": "files/bbc-pol-004.txt"
        }' \
    --settings '{
        "classifier": "Azure OpenAI",
        "classificationBins": [
            "business", "entertainment", "politics", "sports", "tech"
            ],
        "action": "copy",
        "useCache": false,
        "outputFolder": "classified"
        }' \
    --workflow-id '00000000-0000-0000-0000-000000000000' \
    --log-level DEBUG

```

### Currently supported classifiers 

-   Azure OpenAI
    -   Environment variables required:
        -   `OPENAI_API_KEY`
        -   `OPENAI_API_BASE`
        -   `OPENAI_API_VERSION`
        -   `OPENAI_API_ENGINE`
        -   `OPENAI_API_MODEL`

**Make sure the required environment variables are set before testing**

### Testing the tool from its docker image

To test the tool from its docker image, run the following command:

```commandline
docker run \
    -v /Users/arun/Devel/pandora_storage:/mnt/unstract/fs_input \
    unstract-tool-fileops:0.1 \
    python main.py \
    --command RUN \
    --params '{
        "input_file": "files/bbc-pol-004.txt"
        }' \
    --settings '{
        "classifier": "Azure OpenAI",
        "classificationBins": [
            "business", "entertainment", "politics", "sports", "tech"
            ],
        "action": "copy",
        "useCache": false,
        "outputFolder": "classified"
        }' \
    --workflow-id '00000000-0000-0000-0000-000000000000' \
    --log-level DEBUG

```

Notes for Docker:

* The `-v` option mounts the `/Users/arun/Devel/pandora_storage` folder on the host machine to
  the `/mnt/unstract/fs_input`. Replace the path with the path to your documents folder.
* When this command is called by the workflow execution subsystem, the path to the input files configured by the user in
  the UI is automatically mounted and loaded as a volumne in the `/mnt/unstract/fs_input` folder in the container.