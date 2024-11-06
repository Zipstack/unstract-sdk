import enum


class FileStorageProvider(enum.Enum):
    Azure = "azure"
    GCS = "gcs"
    S3 = "s3"
    Minio = "s3"
    Redis = "redis"
    Local = "local"
