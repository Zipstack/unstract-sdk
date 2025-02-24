import json
import os.path
from json import JSONDecodeError

import pytest
from dotenv import load_dotenv

from unstract.sdk.file_storage import FileStorageProvider, PermanentFileStorage

load_dotenv()


class TEST_CONSTANTS:
    READ_FOLDER_PATH = os.environ.get("READ_FOLDER_PATH")
    WRITE_FOLDER_PATH = os.environ.get("WRITE_FOLDER_PATH")
    RECURSION_FOLDER_PATH = os.environ.get("RECURSION_FOLDER_PATH")
    READ_PDF_FILE = os.environ.get("READ_PDF_FILE")
    READ_TEXT_FILE = os.environ.get("READ_TEXT_FILE")
    WRITE_PDF_FILE = os.environ.get("WRITE_PDF_FILE")
    WRITE_TEXT_FILE = os.environ.get("WRITE_TEXT_FILE")
    TEST_FOLDER = os.environ.get("TEST_FOLDER")
    GCS_BUCKET = os.environ.get("GCS_BUCKET")
    TEXT_CONTENT = os.environ.get("TEXT_CONTENT")
    FILE_STORAGE_GCS = "FILE_STORAGE_GCS"
    FILE_STORAGE_MINIO = "FILE_STORAGE_MINIO"
    FILE_STORAGE_LOCAL = "FILE_STORAGE_LOCAL"


def permanent_file_storage(provider: FileStorageProvider):
    try:
        if provider == FileStorageProvider.GCS:
            creds = json.loads(os.environ.get(TEST_CONSTANTS.FILE_STORAGE_GCS, "{}"))
        elif provider == FileStorageProvider.LOCAL:
            creds = json.loads(os.environ.get(TEST_CONSTANTS.FILE_STORAGE_LOCAL, "{}"))
        elif provider == FileStorageProvider.MINIO:
            creds = json.loads(os.environ.get(TEST_CONSTANTS.FILE_STORAGE_MINIO, "{}"))
    except JSONDecodeError:
        creds = {}
    file_storage = PermanentFileStorage(provider=provider, **creds)
    assert file_storage is not None
    return file_storage


@pytest.mark.parametrize(
    "file_storage, file_read_path, read_mode",
    [
        (
            permanent_file_storage(provider=FileStorageProvider.GCS),
            "fsspec-test/input/3.txt",
            "r",
        ),
        (
            permanent_file_storage(provider=FileStorageProvider.MINIO),
            "fsspec-test/input/3.txt",
            "r",
        ),
        (
            permanent_file_storage(provider=FileStorageProvider.AZURE),
            "fsspec-test/input/3.txt",
            "r",
        ),
    ],
)
def test_permanent_fs_copy_on_read(file_storage, file_read_path, read_mode):
    if file_storage.exists(file_read_path):
        file_storage.rm(file_read_path)
    with pytest.raises(FileNotFoundError):
        file_storage.read(
            file_read_path,
            read_mode,
        )


@pytest.mark.parametrize(
    "file_storage, file_read_path, read_mode, legacy_storage_path, "
    "file_write_path, write_mode",
    [
        (
            permanent_file_storage(provider=FileStorageProvider.GCS),
            "fsspec-test/input/3.txt",
            "r",
            "fsspec-test/legacy_storage/3.txt",
            "fsspec-test/output/copy_on_read_legacy_storage.txt",
            "w",
        ),
        (
            permanent_file_storage(provider=FileStorageProvider.MINIO),
            "fsspec-test/input/3.txt",
            "r",
            "fsspec-test/legacy_storage/3.txt",
            "fsspec-test/output/copy_on_read_legacy_storage.txt",
            "w",
        ),
        (
            permanent_file_storage(provider=FileStorageProvider.AZURE),
            "fsspec-test/input/3.txt",
            "r",
            "fsspec-test/legacy_storage/3.txt",
            "fsspec-test/output/copy_on_read_legacy_storage.txt",
            "w",
        ),
    ],
)
def test_permanent_fs_copy_on_read_with_legacy_storage(
    file_storage,
    file_read_path,
    read_mode,
    legacy_storage_path,
    file_write_path,
    write_mode,
):
    if file_storage.exists(file_read_path):
        file_storage.rm(file_read_path)
    file_read_contents = file_storage.read(
        file_read_path, read_mode, legacy_storage_path=legacy_storage_path
    )
    print(file_read_contents)
    if file_storage.exists(file_write_path):
        file_storage.rm(file_write_path)
    file_storage.write(file_write_path, write_mode, data=file_read_contents)

    file_write_contents = file_storage.read(file_write_path, read_mode)
    assert len(file_read_contents) == len(file_write_contents)


@pytest.mark.parametrize(
    "file_storage, file_read_path, read_mode, file_write_path, write_mode",
    [
        (
            permanent_file_storage(provider=FileStorageProvider.LOCAL),
            "fsspec-test/input/3.txt",
            "r",
            "fsspec-test/output/copy_on_write.txt",
            "w",
        ),
    ],
)
def test_permanent_fs_copy(
    file_storage, file_read_path, read_mode, file_write_path, write_mode
):
    file_read_contents = file_storage.read(file_read_path, read_mode)
    print(file_read_contents)
    if file_storage.exists(file_write_path):
        file_storage.rm(file_write_path)
    file_storage.write(file_write_path, write_mode, data=file_read_contents)
    file_write_contents = file_storage.read(file_write_path, read_mode)
    assert len(file_read_contents) == len(file_write_contents)


@pytest.mark.parametrize(
    "file_storage, from_path, read_mode, to_path, write_mode",
    [
        (
            permanent_file_storage(provider=FileStorageProvider.GCS),
            "fsspec-test/input/3.txt",
            "r",
            "fsspec-test/output/test_write.txt",
            "w",
        ),
        (
            permanent_file_storage(provider=FileStorageProvider.MINIO),
            "fsspec-test/input/3.txt",
            "r",
            "fsspec-test/output/test_write.txt",
            "w",
        ),
        (
            permanent_file_storage(provider=FileStorageProvider.AZURE),
            "fsspec-test/input/3.txt",
            "r",
            "fsspec-test/output/test_write.txt",
            "w",
        ),
    ],
)
def test_permanent_fs_download(file_storage, from_path, read_mode, to_path, write_mode):
    file_read_contents = file_storage.read(from_path, read_mode)
    print(file_read_contents)
    file_storage.download(from_path, to_path)
    local_file_storage = permanent_file_storage(provider=FileStorageProvider.LOCAL)
    file_write_contents = local_file_storage.read(to_path, read_mode)
    assert len(file_read_contents) == len(file_write_contents)


@pytest.mark.parametrize(
    "provider",
    [(FileStorageProvider.GCS), (FileStorageProvider.LOCAL)],
)
def test_permanent_supported_file_storage_mode(provider):
    file_storage = permanent_file_storage(provider=provider)
    assert file_storage is not None and isinstance(file_storage, PermanentFileStorage)
