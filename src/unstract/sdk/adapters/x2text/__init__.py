from unstract.sdk.adapters import AdapterDict
from unstract.sdk.adapters.x2text.register import X2TextRegistry

adapters: AdapterDict = {}
X2TextRegistry.register_adapters(adapters)
