# Bedrock LiteLLM Adapter

This adapter provides integration with AWS Bedrock using LiteLLM. It provides a clean interface for making completion and chat requests to Bedrock models.

## Configuration

The adapter requires the following configuration:

- `model`: The Bedrock model to use
- `aws_access_key_id`: AWS access key ID
- `aws_secret_access_key`: AWS secret access key
- `region_name`: AWS region name
- `timeout` (optional): Request timeout in seconds (default: 900)
- `max_retries` (optional): Maximum number of retries (default: 3)
- `max_tokens` (optional): Maximum tokens to generate (default: 512)

## Usage

```python
from unstract.sdk.adapters.llm_litellm.bedrock import BedrockAdapter

# Initialize adapter
adapter = BedrockAdapter({
    "model": "anthropic.claude-v2",
    "aws_access_key_id": "your_access_key",
    "aws_secret_access_key": "your_secret_key",
    "region_name": "us-west-2"
})

# Get LLM instance
llm = adapter.get_llm_instance()

# Simple completion
response = llm.complete("Your prompt here")
print(response["text"])

# Streaming completion
for chunk in llm.stream_complete("Your prompt here"):
    print(chunk["text"], end="")

# Chat completion
messages = [
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": "Hello!"}
]
response = llm.chat(messages)
print(response["text"])
```
