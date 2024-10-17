import enum


class FileStorageType(enum.Enum):
    Azure = 1
    GCS = "gcs"
    S3 = 3
    Minio = 4
    Redis = 5
    Local = "local"
