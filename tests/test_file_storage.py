import io
import json
import os.path
from json import JSONDecodeError

import pdfplumber
import pytest
from dotenv import load_dotenv

from unstract.sdk.constants import MimeType
from unstract.sdk.exceptions import FileOperationError
from unstract.sdk.file_storage.constants import FileOperationParams, StorageType
from unstract.sdk.file_storage.env_helper import EnvHelper
from unstract.sdk.file_storage.impl import FileStorage
from unstract.sdk.file_storage.provider import FileStorageProvider

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
    FILE_STORAGE_S3 = "FILE_STORAGE_S3"
    FILE_STORAGE_AZURE = "FILE_STORAGE_AZURE"


def file_storage(provider: FileStorageProvider):
    try:
        if provider == FileStorageProvider.GCS:
            creds = json.loads(os.environ.get(TEST_CONSTANTS.FILE_STORAGE_GCS, "{}"))
        elif provider == FileStorageProvider.MINIO:
            creds = json.loads(os.environ.get(TEST_CONSTANTS.FILE_STORAGE_MINIO, "{}"))
        elif provider == FileStorageProvider.LOCAL:
            creds = json.loads(os.environ.get(TEST_CONSTANTS.FILE_STORAGE_LOCAL, "{}"))
        elif provider == FileStorageProvider.S3:
            creds = json.loads(os.environ.get(TEST_CONSTANTS.FILE_STORAGE_S3, "{}"))
        elif provider == FileStorageProvider.AZURE:
            creds = json.loads(os.environ.get(TEST_CONSTANTS.FILE_STORAGE_AZURE, "{}"))
    except JSONDecodeError:
        creds = {}
    file_storage = FileStorage(provider, **creds)
    assert file_storage is not None
    return file_storage


@pytest.mark.parametrize(
    "file_storage, path, mode, read_length, expected_read_length",
    [
        (
            file_storage(provider=FileStorageProvider.GCS),
            TEST_CONSTANTS.READ_PDF_FILE,
            "rb",
            -1,
            os.path.getsize(TEST_CONSTANTS.READ_PDF_FILE),
        ),
        (
            file_storage(provider=FileStorageProvider.LOCAL),
            TEST_CONSTANTS.READ_TEXT_FILE,
            "rb",
            0,
            0,
        ),
        (
            file_storage(provider=FileStorageProvider.LOCAL),
            TEST_CONSTANTS.READ_TEXT_FILE,
            "r",
            -1,
            os.path.getsize(TEST_CONSTANTS.READ_TEXT_FILE),
        ),
        (
            file_storage(provider=FileStorageProvider.MINIO),
            TEST_CONSTANTS.READ_TEXT_FILE,
            "rb",
            0,
            0,
        ),
        (
            file_storage(provider=FileStorageProvider.MINIO),
            TEST_CONSTANTS.READ_TEXT_FILE,
            "r",
            -1,
            os.path.getsize(TEST_CONSTANTS.READ_TEXT_FILE),
        ),
        (
            file_storage(provider=FileStorageProvider.S3),
            TEST_CONSTANTS.READ_TEXT_FILE,
            "rb",
            0,
            os.path.getsize(TEST_CONSTANTS.READ_TEXT_FILE),
        ),
        (
            file_storage(provider=FileStorageProvider.AZURE),
            TEST_CONSTANTS.READ_TEXT_FILE,
            "rb",
            0,
            os.path.getsize(TEST_CONSTANTS.READ_TEXT_FILE),
        ),
    ],
)
def test_file_read(file_storage, path, mode, read_length, expected_read_length):
    file_contents = file_storage.read(path=path, mode=mode, length=read_length)
    assert len(file_contents) == expected_read_length


@pytest.mark.parametrize(
    "file_storage, path, mode, read_length",
    [
        (
            file_storage(provider=FileStorageProvider.LOCAL),
            "1.txt",
            "rb",
            -1,
        ),
    ],
)
def test_file_read_exception(file_storage, path, mode, read_length):
    with pytest.raises(FileNotFoundError):
        file_storage.read(path=path, mode=mode, length=read_length)


@pytest.mark.parametrize(
    "file_storage, read_file_path, read_mode, file_contents, "
    "write_file_path, write_mode, read_length, expected_write_length",
    [
        (
            file_storage(provider=FileStorageProvider.GCS),
            TEST_CONSTANTS.READ_PDF_FILE,
            "rb",
            None,
            TEST_CONSTANTS.WRITE_PDF_FILE,
            "wb",
            -1,
            os.path.getsize(TEST_CONSTANTS.READ_PDF_FILE),
        ),
        (
            file_storage(provider=FileStorageProvider.GCS),
            TEST_CONSTANTS.READ_TEXT_FILE,
            "rb",
            None,
            TEST_CONSTANTS.WRITE_TEXT_FILE,
            "wb",
            0,
            0,
        ),
        (
            file_storage(provider=FileStorageProvider.GCS),
            TEST_CONSTANTS.READ_TEXT_FILE,
            "rb",
            None,
            TEST_CONSTANTS.WRITE_TEXT_FILE,
            "wb",
            0,
            0,
        ),
        (
            file_storage(provider=FileStorageProvider.LOCAL),
            TEST_CONSTANTS.READ_PDF_FILE,
            "rb",
            None,
            TEST_CONSTANTS.WRITE_PDF_FILE,
            "wb",
            -1,
            os.path.getsize(TEST_CONSTANTS.READ_PDF_FILE),
        ),
        (
            file_storage(provider=FileStorageProvider.LOCAL),
            TEST_CONSTANTS.READ_TEXT_FILE,
            "rb",
            None,
            TEST_CONSTANTS.WRITE_TEXT_FILE,
            "wb",
            -1,
            os.path.getsize(TEST_CONSTANTS.READ_TEXT_FILE),
        ),
        (
            file_storage(provider=FileStorageProvider.LOCAL),
            TEST_CONSTANTS.READ_TEXT_FILE,
            "rb",
            None,
            TEST_CONSTANTS.WRITE_TEXT_FILE,
            "wb",
            0,
            0,
        ),
        (
            file_storage(provider=FileStorageProvider.GCS),
            None,
            "rb",
            TEST_CONSTANTS.TEXT_CONTENT,
            TEST_CONSTANTS.WRITE_TEXT_FILE,
            "w",
            0,
            len(TEST_CONSTANTS.TEXT_CONTENT),
        ),
        (
            file_storage(provider=FileStorageProvider.LOCAL),
            None,
            "rb",
            TEST_CONSTANTS.TEXT_CONTENT.encode(),
            TEST_CONSTANTS.WRITE_TEXT_FILE,
            "wb",
            0,
            len(TEST_CONSTANTS.TEXT_CONTENT.encode()),
        ),
        (
            file_storage(provider=FileStorageProvider.MINIO),
            TEST_CONSTANTS.READ_PDF_FILE,
            "rb",
            None,
            TEST_CONSTANTS.WRITE_PDF_FILE,
            "wb",
            -1,
            os.path.getsize(TEST_CONSTANTS.READ_PDF_FILE),
        ),
        (
            file_storage(provider=FileStorageProvider.MINIO),
            TEST_CONSTANTS.READ_TEXT_FILE,
            "rb",
            None,
            TEST_CONSTANTS.WRITE_TEXT_FILE,
            "wb",
            0,
            0,
        ),
        (
            file_storage(provider=FileStorageProvider.MINIO),
            TEST_CONSTANTS.READ_TEXT_FILE,
            "rb",
            None,
            TEST_CONSTANTS.WRITE_TEXT_FILE,
            "wb",
            0,
            0,
        ),
        (
            file_storage(provider=FileStorageProvider.MINIO),
            None,
            "rb",
            TEST_CONSTANTS.TEXT_CONTENT,
            TEST_CONSTANTS.WRITE_TEXT_FILE,
            "w",
            0,
            len(TEST_CONSTANTS.TEXT_CONTENT),
        ),
        (
            file_storage(provider=FileStorageProvider.AZURE),
            TEST_CONSTANTS.READ_PDF_FILE,
            "rb",
            None,
            TEST_CONSTANTS.WRITE_PDF_FILE,
            "wb",
            -1,
            os.path.getsize(TEST_CONSTANTS.READ_PDF_FILE),
        ),
        (
            file_storage(provider=FileStorageProvider.AZURE),
            TEST_CONSTANTS.READ_TEXT_FILE,
            "rb",
            None,
            TEST_CONSTANTS.WRITE_TEXT_FILE,
            "wb",
            0,
            0,
        ),
        (
            file_storage(provider=FileStorageProvider.AZURE),
            TEST_CONSTANTS.READ_TEXT_FILE,
            "rb",
            None,
            TEST_CONSTANTS.WRITE_TEXT_FILE,
            "wb",
            0,
            0,
        ),
        (
            file_storage(provider=FileStorageProvider.AZURE),
            None,
            "rb",
            TEST_CONSTANTS.TEXT_CONTENT,
            TEST_CONSTANTS.WRITE_TEXT_FILE,
            "w",
            0,
            len(TEST_CONSTANTS.TEXT_CONTENT),
        ),
    ],
)
def test_file_write(
    file_storage,
    read_file_path,
    read_mode,
    file_contents,
    write_file_path,
    write_mode,
    read_length,
    expected_write_length,
):
    if file_storage.exists(path=TEST_CONSTANTS.WRITE_FOLDER_PATH):
        file_storage.rm(path=TEST_CONSTANTS.WRITE_FOLDER_PATH, recursive=True)
    assert file_storage.exists(path=TEST_CONSTANTS.WRITE_FOLDER_PATH) is False
    file_storage.mkdir(path=TEST_CONSTANTS.WRITE_FOLDER_PATH)
    # assert file_storage.path_exists(path=TEST_CONSTANTS.WRITE_FOLDER_PATH) == True
    if read_file_path:
        file_contents = file_storage.read(
            path=read_file_path, mode=read_mode, length=read_length
        )
    else:
        file_contents = file_contents
    bytes_written = file_storage.write(
        path=write_file_path, mode=write_mode, data=file_contents
    )
    assert bytes_written == expected_write_length


@pytest.mark.parametrize(
    "file_storage, folder_path, expected_result",
    [
        (
            file_storage(provider=FileStorageProvider.GCS),
            TEST_CONSTANTS.TEST_FOLDER,
            False,  # mkdir does not work for blob storages
            # as they only support creating buckets. For
            # further details pls check implementation of mkdir in GCSFS
        ),
        (
            file_storage(provider=FileStorageProvider.LOCAL),
            TEST_CONSTANTS.TEST_FOLDER,
            True,
        ),
        (
            file_storage(provider=FileStorageProvider.MINIO),
            TEST_CONSTANTS.TEST_FOLDER,
            False,  # mkdir does not work for blob storages
            # as they only support creating buckets. For
            # further details pls check implementation of mkdir in S3
        ),
        (
            file_storage(provider=FileStorageProvider.AZURE),
            TEST_CONSTANTS.TEST_FOLDER,
            False,
        ),
    ],
)
def test_make_dir(file_storage, folder_path, expected_result):
    if file_storage.exists(path=folder_path):
        file_storage.rm(path=folder_path, recursive=True)
    file_storage.mkdir(folder_path)
    assert file_storage.exists(path=folder_path) == expected_result


@pytest.mark.parametrize(
    "file_storage, folder_path, expected_result",
    [
        (
            file_storage(provider=FileStorageProvider.GCS),
            TEST_CONSTANTS.GCS_BUCKET,
            True,
        ),
        (
            file_storage(provider=FileStorageProvider.LOCAL),
            TEST_CONSTANTS.TEST_FOLDER,
            True,
        ),
        (
            file_storage(provider=FileStorageProvider.LOCAL),
            "dummy",
            False,
        ),
        (
            file_storage(provider=FileStorageProvider.MINIO),
            TEST_CONSTANTS.GCS_BUCKET,
            True,
        ),
        (
            file_storage(provider=FileStorageProvider.AZURE),
            TEST_CONSTANTS.GCS_BUCKET,
            True,
        ),
    ],
)
def test_path_exists(file_storage, folder_path, expected_result):
    assert file_storage.exists(path=folder_path) == expected_result


@pytest.mark.parametrize(
    "file_storage, folder_path, expected_file_count",
    [
        (
            file_storage(provider=FileStorageProvider.GCS),
            TEST_CONSTANTS.READ_FOLDER_PATH,
            3,
        ),
        (
            file_storage(provider=FileStorageProvider.LOCAL),
            TEST_CONSTANTS.READ_FOLDER_PATH,
            3,
        ),
        (
            file_storage(provider=FileStorageProvider.LOCAL),
            TEST_CONSTANTS.READ_TEXT_FILE,
            1,
        ),
        (
            file_storage(provider=FileStorageProvider.MINIO),
            TEST_CONSTANTS.READ_FOLDER_PATH,
            2,
        ),
        (
            file_storage(provider=FileStorageProvider.AZURE),
            TEST_CONSTANTS.READ_FOLDER_PATH,
            2,
        ),
    ],
)
def test_ls(file_storage, folder_path, expected_file_count):
    assert len(file_storage.ls(folder_path)) == expected_file_count


@pytest.mark.parametrize(
    "file_storage, folder_path",
    [
        (
            file_storage(provider=FileStorageProvider.GCS),
            TEST_CONSTANTS.WRITE_FOLDER_PATH,
        ),
        (
            file_storage(provider=FileStorageProvider.LOCAL),
            TEST_CONSTANTS.WRITE_FOLDER_PATH,
        ),
        (
            file_storage(provider=FileStorageProvider.MINIO),
            TEST_CONSTANTS.WRITE_FOLDER_PATH,
        ),
        (
            file_storage(provider=FileStorageProvider.AZURE),
            TEST_CONSTANTS.WRITE_FOLDER_PATH,
        ),
    ],
)
def test_rm(file_storage, folder_path):
    if not file_storage.exists(path=folder_path):
        file_storage.mkdir(path=folder_path)
        if not file_storage.exists(path=folder_path):
            file_storage.fs.touch(path=folder_path)
    file_storage.rm(path=folder_path)
    assert file_storage.exists(path=folder_path) is False


@pytest.mark.parametrize(
    "file_storage, folder_path, recursive, test_folder_path",
    [
        (
            file_storage(provider=FileStorageProvider.LOCAL),
            TEST_CONSTANTS.RECURSION_FOLDER_PATH,
            True,
            TEST_CONSTANTS.WRITE_FOLDER_PATH,
        ),
    ],
)
def test_rm_recursive(file_storage, folder_path, recursive, test_folder_path):
    if not file_storage.exists(path=folder_path):
        file_storage.mkdir(path=folder_path)
    assert file_storage.exists(path=folder_path) is True
    file_storage.rm(path=test_folder_path, recursive=recursive)
    assert file_storage.exists(path=test_folder_path) is False


@pytest.mark.parametrize(
    "file_storage, folder_path, recursive, test_folder_path",
    [
        (
            file_storage(provider=FileStorageProvider.LOCAL),
            TEST_CONSTANTS.RECURSION_FOLDER_PATH,
            False,
            TEST_CONSTANTS.WRITE_FOLDER_PATH,
        ),
    ],
)
def test_rm_recursive_exception(file_storage, folder_path, recursive, test_folder_path):
    if not file_storage.exists(path=folder_path):
        file_storage.mkdir(path=folder_path)
    assert file_storage.exists(path=folder_path) is True
    with pytest.raises(FileOperationError):
        file_storage.rm(path=test_folder_path, recursive=recursive)


@pytest.mark.parametrize(
    "file_storage, file_path, mode, location, whence, expected_size",
    [
        (
            file_storage(provider=FileStorageProvider.GCS),
            TEST_CONSTANTS.READ_TEXT_FILE,
            "rb",
            1,
            0,
            os.path.getsize(TEST_CONSTANTS.READ_TEXT_FILE) - 1,
        ),
        (
            file_storage(provider=FileStorageProvider.GCS),
            TEST_CONSTANTS.READ_PDF_FILE,
            "r",
            0,
            2,
            0,
        ),
        (
            file_storage(provider=FileStorageProvider.LOCAL),
            TEST_CONSTANTS.READ_TEXT_FILE,
            "rb",
            1,
            0,
            os.path.getsize(TEST_CONSTANTS.READ_TEXT_FILE) - 1,
        ),
        (
            file_storage(provider=FileStorageProvider.LOCAL),
            TEST_CONSTANTS.READ_PDF_FILE,
            "r",
            0,
            2,
            0,
        ),
        (
            file_storage(provider=FileStorageProvider.MINIO),
            TEST_CONSTANTS.READ_TEXT_FILE,
            "rb",
            1,
            0,
            os.path.getsize(TEST_CONSTANTS.READ_TEXT_FILE) - 1,
        ),
        (
            file_storage(provider=FileStorageProvider.MINIO),
            TEST_CONSTANTS.READ_PDF_FILE,
            "r",
            0,
            2,
            0,
        ),
    ],
)
def test_seek_file(file_storage, file_path, mode, location, whence, expected_size):
    seek_position = file_storage.seek(file_path, location, whence)
    file_contents = file_storage.read(
        path=file_path, mode=mode, seek_position=seek_position
    )
    print(file_contents)
    assert len(file_contents) == expected_size


@pytest.mark.parametrize("provider", [(FileStorageProvider.GCS)])
def test_file(provider):
    os.environ.clear()
    file_storage = FileStorage(provider=provider)
    assert file_storage is not None
    with pytest.raises(FileOperationError):
        file_storage.exists(TEST_CONSTANTS.READ_PDF_FILE)
    load_dotenv()


@pytest.mark.parametrize(
    "file_storage, lpath, rpath, recursive, expected_result",
    [
        (
            file_storage(provider=FileStorageProvider.GCS),
            TEST_CONSTANTS.READ_TEXT_FILE,
            TEST_CONSTANTS.TEST_FOLDER,
            True,
            True,
        ),
        (
            file_storage(provider=FileStorageProvider.LOCAL),
            TEST_CONSTANTS.READ_TEXT_FILE,
            TEST_CONSTANTS.TEST_FOLDER,
            True,
            True,
        ),
        (
            file_storage(provider=FileStorageProvider.LOCAL),
            TEST_CONSTANTS.READ_FOLDER_PATH,
            TEST_CONSTANTS.TEST_FOLDER,
            True,
            True,
        ),
        (
            file_storage(provider=FileStorageProvider.LOCAL),
            TEST_CONSTANTS.READ_FOLDER_PATH,
            TEST_CONSTANTS.TEST_FOLDER,
            False,
            False,
        ),
        (
            file_storage(provider=FileStorageProvider.MINIO),
            TEST_CONSTANTS.READ_TEXT_FILE,
            TEST_CONSTANTS.TEST_FOLDER,
            True,
            True,
        ),
    ],
)
def test_cp(file_storage, lpath, rpath, recursive, expected_result):
    file_storage.cp(lpath, rpath, recursive=recursive, overwrite=True)
    actual_result = file_storage.exists(rpath)
    assert actual_result == expected_result
    if actual_result:
        file_storage.rm(rpath, recursive=True)
    assert file_storage.exists(rpath) is False


def test_pdf_read():
    fs = file_storage(FileStorageProvider.LOCAL)
    pdf_contents = io.BytesIO(fs.read(path=TEST_CONSTANTS.READ_PDF_FILE, mode="rb"))
    page_count = 0
    with pdfplumber.open(pdf_contents) as pdf:
        # calculate the number of pages
        page_count = len(pdf.pages)
        print(f"Page count: {page_count}")
    assert page_count == 7


@pytest.mark.parametrize(
    "file_storage, path, expected_size",
    [
        (
            file_storage(provider=FileStorageProvider.GCS),
            TEST_CONSTANTS.READ_PDF_FILE,
            os.path.getsize(TEST_CONSTANTS.READ_PDF_FILE),
        ),
        (
            file_storage(provider=FileStorageProvider.GCS),
            TEST_CONSTANTS.READ_TEXT_FILE,
            os.path.getsize(TEST_CONSTANTS.READ_TEXT_FILE),
        ),
        (
            file_storage(provider=FileStorageProvider.GCS),
            TEST_CONSTANTS.READ_PDF_FILE,
            os.path.getsize(TEST_CONSTANTS.READ_PDF_FILE),
        ),
        (
            file_storage(provider=FileStorageProvider.LOCAL),
            TEST_CONSTANTS.READ_TEXT_FILE,
            os.path.getsize(TEST_CONSTANTS.READ_TEXT_FILE),
        ),
        (
            file_storage(provider=FileStorageProvider.MINIO),
            TEST_CONSTANTS.READ_TEXT_FILE,
            os.path.getsize(TEST_CONSTANTS.READ_TEXT_FILE),
        ),
        (
            file_storage(provider=FileStorageProvider.MINIO),
            TEST_CONSTANTS.READ_PDF_FILE,
            os.path.getsize(TEST_CONSTANTS.READ_PDF_FILE),
        ),
    ],
)
def test_file_size(file_storage, path, expected_size):
    file_size = file_storage.size(path=path)
    assert file_size == expected_size


@pytest.mark.parametrize(
    "file_storage, path, read_length, expected_mime_type",
    [
        (
            file_storage(provider=FileStorageProvider.GCS),
            TEST_CONSTANTS.READ_PDF_FILE,
            FileOperationParams.READ_ENTIRE_LENGTH,
            MimeType.PDF,
        ),
        (
            file_storage(provider=FileStorageProvider.GCS),
            TEST_CONSTANTS.READ_TEXT_FILE,
            FileOperationParams.READ_ENTIRE_LENGTH,
            MimeType.TEXT,
        ),
        (
            file_storage(provider=FileStorageProvider.GCS),
            TEST_CONSTANTS.READ_PDF_FILE,
            FileOperationParams.READ_ENTIRE_LENGTH,
            MimeType.PDF,
        ),
        (
            file_storage(provider=FileStorageProvider.LOCAL),
            TEST_CONSTANTS.READ_TEXT_FILE,
            50,
            MimeType.TEXT,
        ),
        (
            file_storage(provider=FileStorageProvider.MINIO),
            TEST_CONSTANTS.READ_PDF_FILE,
            100,
            MimeType.PDF,
        ),
        (
            file_storage(provider=FileStorageProvider.MINIO),
            TEST_CONSTANTS.READ_TEXT_FILE,
            100,
            MimeType.TEXT,
        ),
        (
            file_storage(provider=FileStorageProvider.MINIO),
            TEST_CONSTANTS.READ_PDF_FILE,
            100,
            MimeType.PDF,
        ),
    ],
)
def test_file_mime_type(file_storage, path, read_length, expected_mime_type):
    mime_type = file_storage.mime_type(path=path)
    file_storage.mkdir(path=TEST_CONSTANTS.READ_FOLDER_PATH)
    assert mime_type == expected_mime_type
    mime_type_read_length = file_storage.mime_type(path=path, read_length=read_length)
    file_storage.mkdir(path=TEST_CONSTANTS.READ_FOLDER_PATH)
    assert mime_type_read_length == expected_mime_type


@pytest.mark.parametrize(
    "file_storage, from_path, to_path",
    [
        (
            file_storage(provider=FileStorageProvider.GCS),
            TEST_CONSTANTS.READ_TEXT_FILE,
            TEST_CONSTANTS.TEST_FOLDER + "/1.txt",
        ),
        (
            file_storage(provider=FileStorageProvider.LOCAL),
            TEST_CONSTANTS.READ_TEXT_FILE,
            TEST_CONSTANTS.TEST_FOLDER + "/2.txt",
        ),
        (
            file_storage(provider=FileStorageProvider.MINIO),
            TEST_CONSTANTS.READ_TEXT_FILE,
            TEST_CONSTANTS.TEST_FOLDER + "/3.txt",
        ),
        (
            file_storage(provider=FileStorageProvider.AZURE),
            TEST_CONSTANTS.READ_TEXT_FILE,
            TEST_CONSTANTS.TEST_FOLDER + "/3.txt",
        ),
    ],
)
def test_download(file_storage, from_path, to_path):
    local_file_storage = FileStorage(FileStorageProvider.LOCAL)
    if local_file_storage.exists(to_path):
        local_file_storage.rm(to_path, recursive=True)
    assert local_file_storage.exists(to_path) is False
    file_storage.download(from_path, to_path)
    assert local_file_storage.exists(to_path) is True


@pytest.mark.parametrize(
    "file_storage, from_path, to_path",
    [
        (
            file_storage(provider=FileStorageProvider.GCS),
            TEST_CONSTANTS.READ_TEXT_FILE,
            TEST_CONSTANTS.TEST_FOLDER + "/1.txt",
        ),
        (
            file_storage(provider=FileStorageProvider.LOCAL),
            TEST_CONSTANTS.READ_TEXT_FILE,
            TEST_CONSTANTS.TEST_FOLDER + "/2.txt",
        ),
        (
            file_storage(provider=FileStorageProvider.MINIO),
            TEST_CONSTANTS.READ_TEXT_FILE,
            TEST_CONSTANTS.TEST_FOLDER + "/3.txt",
        ),
        (
            file_storage(provider=FileStorageProvider.AZURE),
            TEST_CONSTANTS.READ_TEXT_FILE,
            TEST_CONSTANTS.TEST_FOLDER + "/3.txt",
        ),
    ],
)
def test_upload(file_storage, from_path, to_path):
    local_file_storage = FileStorage(FileStorageProvider.LOCAL)
    assert local_file_storage.exists(from_path) is True
    if file_storage.exists(to_path):
        file_storage.rm(to_path, recursive=True)
    file_storage.upload(from_path, to_path)
    assert file_storage.exists(to_path) is True


@pytest.mark.parametrize(
    "file_storage, file_path, expected_result",
    [
        (
            file_storage(provider=FileStorageProvider.GCS),
            TEST_CONSTANTS.READ_TEXT_FILE,
            "4a08b5721f75657eb883202cae16c74ca62df2c605e4126e50f4bf341d4fd693",
        ),
        (
            file_storage(provider=FileStorageProvider.LOCAL),
            TEST_CONSTANTS.READ_TEXT_FILE,
            "4a08b5721f75657eb883202cae16c74ca62df2c605e4126e50f4bf341d4fd693",
        ),
        (
            file_storage(provider=FileStorageProvider.MINIO),
            TEST_CONSTANTS.READ_TEXT_FILE,
            "4a08b5721f75657eb883202cae16c74ca62df2c605e4126e50f4bf341d4fd693",
        ),
        (
            file_storage(provider=FileStorageProvider.AZURE),
            TEST_CONSTANTS.READ_TEXT_FILE,
            "4a08b5721f75657eb883202cae16c74ca62df2c605e4126e50f4bf341d4fd693",
        ),
    ],
)
def test_get_hash_from_file(file_storage, file_path, expected_result):
    actual_file_hash = file_storage.get_hash_from_file(file_path)
    assert actual_file_hash == expected_result


@pytest.mark.parametrize(
    "file_storage, folder_path, expected_result",
    [
        (
            file_storage(provider=FileStorageProvider.GCS),
            TEST_CONSTANTS.READ_FOLDER_PATH + "/*.pdf",
            1,
        ),
        (
            file_storage(provider=FileStorageProvider.LOCAL),
            TEST_CONSTANTS.READ_FOLDER_PATH + "/*.txt",
            2,
        ),
        (
            file_storage(provider=FileStorageProvider.MINIO),
            TEST_CONSTANTS.READ_FOLDER_PATH + "/*.pdf",
            1,
        ),
        (
            file_storage(provider=FileStorageProvider.AZURE),
            TEST_CONSTANTS.READ_FOLDER_PATH + "/*.pdf",
            1,
        ),
    ],
)
def test_glob(file_storage, folder_path, expected_result):
    file_list = file_storage.glob(path=folder_path)
    print(f"Files: {file_list}")
    assert len(file_list) == expected_result


@pytest.mark.parametrize(
    "storage_type, env_name, expected",
    [
        (
            StorageType.PERMANENT,
            "TEST_PERMANENT_STORAGE_GCS",
            FileStorageProvider.GCS,
        ),
        (
            StorageType.SHARED_TEMPORARY,
            "TEST_TEMPORARY_STORAGE",
            FileStorageProvider.MINIO,
        ),
        (
            StorageType.PERMANENT,
            "TEST_LOCAL_STORAGE",
            FileStorageProvider.LOCAL,
        ),
        (
            StorageType.PERMANENT,
            "TEST_PERMANENT_STORAGE_AZURE",
            FileStorageProvider.AZURE,
        ),
    ],
)
def test_get_storage(storage_type, env_name, expected):
    file_storage = EnvHelper.get_storage(storage_type, env_name)
    assert file_storage.provider == expected
    print(file_storage)


@pytest.mark.parametrize(
    "storage_type, env_name, path",
    [
        (
            StorageType.PERMANENT,
            "TEST_PERMANENT_STORAGE_GCS",
            "fsspec-test",
        ),
        (
            StorageType.SHARED_TEMPORARY,
            "TEST_TEMPORARY_STORAGE",
            "unstract/execution/mock_org/"
            "13484b52-2127-48c2-b1a3-b517365346c3/"
            "39fcdcba-90bb-44ce-9446-67253adcb4d7/COPY_TO_FOLDER",
        ),
    ],
)
def test_dir_walk(storage_type, env_name, path):
    file_storage = EnvHelper.get_storage(storage_type, env_name)
    try:
        root, dirs, files = next(file_storage.walk(path))
    except StopIteration:
        return []
    for dir_name in dirs:
        print(dir_name)
    for file_name in files:
        print(file_name)
    if storage_type == StorageType.PERMANENT:
        assert len(files) > 0
    elif storage_type == StorageType.SHARED_TEMPORARY:
        assert len(files) == 0


def list_print_dir(file_storage, path, iter_num):
    print(f"PATH: {path}")
    print(f"\nItertion: {iter_num}")
    try:
        root, dirs, files = next(file_storage.walk(path))
    except StopIteration:
        return []
    for dir_name in dirs:
        print(dir_name)
    for file_name in files:
        print(file_name)
    print(f"Files: {files}")


@pytest.mark.parametrize(
    "storage_type, env_name, path",
    [
        (
            StorageType.SHARED_TEMPORARY,
            "TEST_TEMPORARY_STORAGE",
            "unstract/execution/mock_org/"
            "13484b52-2127-48c2-b1a3-b517365346c3/b"
            "f7b3d81-d0aa-4e9e-883d-25dd0f3a6466/COPY_TO_FOLDER",
        ),
    ],
)
def test_dir_ls(storage_type, env_name, path):
    new_file = os.path.join(path, "tmp.txt")
    file_storage = EnvHelper.get_storage(storage_type, env_name)
    if file_storage.exists(new_file):
        file_storage.rm(new_file)
    list_print_dir(file_storage, path, "1")
    file_storage.write(new_file, "w", data="Hello")
    list_print_dir(file_storage, path, "2")
