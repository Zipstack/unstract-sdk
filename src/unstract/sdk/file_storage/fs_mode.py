import enum


class FileStorageMode(enum.Enum):
    Permanent = 1
    SharedTemporary = 2
    NonSharedTemporary = 3
