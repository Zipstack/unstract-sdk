from unstract.sdk.adapters import AdapterDict
from unstract.sdk.adapters.llm.register import LLMRegistry

adapters: AdapterDict = {}
LLMRegistry.register_adapters(adapters)
