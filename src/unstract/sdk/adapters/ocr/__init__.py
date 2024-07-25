from unstract.sdk.adapters import AdapterDict
from unstract.sdk.adapters.ocr.register import OCRRegistry

adapters: AdapterDict = {}
OCRRegistry.register_adapters(adapters)
