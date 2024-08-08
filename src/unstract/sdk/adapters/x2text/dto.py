from dataclasses import dataclass
from typing import Optional


@dataclass
class TextExtractionMetadata:
    whisper_hash: str


@dataclass
class TextExtractionResult:
    extracted_text: str
    extraction_metadata: Optional[TextExtractionMetadata] = None
