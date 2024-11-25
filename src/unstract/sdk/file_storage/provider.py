import enum


class FileStorageProvider(enum.Enum):
    AZURE = "azure"
    GCS = "gcs"
    S3 = "s3"
    MINIO = "minio"
    REDIS = "redis"
    LOCAL = "local"
