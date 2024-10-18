import enum


class FileStorageProvider(enum.Enum):
    Azure = "azure"
    GCS = "gcs"
    S3 = "s3"
    Minio = "minio"
    Redis = "redis"
    Local = "local"
