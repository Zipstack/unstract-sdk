from enum import Enum


class FileOperationParams:
    READ_ENTIRE_LENGTH = -1
    MIME_TYPE_DEFAULT_READ_LENGTH = 100
    DEFAULT_ENCODING = "utf-8"


class FileSeekPosition:
    START = 0
    CURRENT = 1
    END = 2


class StorageType(Enum):
    PERMANENT = "permanent"
    TEMPORARY = "temporary"


class CredentialKeyword:
    PROVIDER = "provider"
    CREDENTIALS = "credentials"
