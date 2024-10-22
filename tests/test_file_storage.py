import io
import json
import os.path

import pdfplumber
import pytest
from dotenv import load_dotenv

from unstract.sdk.exceptions import FileOperationError, FileStorageError
from unstract.sdk.file_storage import FileStorage, FileStorageProvider
from unstract.sdk.file_storage.fs_permanent import PermanentFileStorage

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
    FILE_STORAGE_ENV = "FILE_STORAGE"


def file_storage(provider: FileStorageProvider):
    credentials = json.loads(os.environ.get(TEST_CONSTANTS.FILE_STORAGE_ENV))
    file_storage = FileStorage(provider=provider, credentials=credentials)
    assert file_storage is not None
    return file_storage


def permanent_file_storage(provider: FileStorageProvider):
    credentials = json.loads(os.environ.get(TEST_CONSTANTS.FILE_STORAGE_ENV))
    file_storage = PermanentFileStorage(provider=provider, credentials=credentials)
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
            file_storage(provider=FileStorageProvider.Local),
            TEST_CONSTANTS.READ_TEXT_FILE,
            "rb",
            0,
            0,
        ),
        (
            file_storage(provider=FileStorageProvider.Local),
            TEST_CONSTANTS.READ_TEXT_FILE,
            "r",
            -1,
            os.path.getsize(TEST_CONSTANTS.READ_TEXT_FILE),
        ),
    ],
)
def test_file_read(file_storage, path, mode, read_length, expected_read_length):
    file_contents = file_storage.read(path=path, mode=mode, length=read_length)
    assert len(file_contents) == expected_read_length


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
            file_storage(provider=FileStorageProvider.Local),
            TEST_CONSTANTS.READ_PDF_FILE,
            "rb",
            None,
            TEST_CONSTANTS.WRITE_PDF_FILE,
            "wb",
            -1,
            os.path.getsize(TEST_CONSTANTS.READ_PDF_FILE),
        ),
        (
            file_storage(provider=FileStorageProvider.Local),
            TEST_CONSTANTS.READ_TEXT_FILE,
            "rb",
            None,
            TEST_CONSTANTS.WRITE_TEXT_FILE,
            "wb",
            -1,
            os.path.getsize(TEST_CONSTANTS.READ_TEXT_FILE),
        ),
        (
            file_storage(provider=FileStorageProvider.Local),
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
            file_storage(provider=FileStorageProvider.Local),
            None,
            "rb",
            TEST_CONSTANTS.TEXT_CONTENT.encode(),
            TEST_CONSTANTS.WRITE_TEXT_FILE,
            "wb",
            0,
            len(TEST_CONSTANTS.TEXT_CONTENT.encode()),
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
            file_storage(provider=FileStorageProvider.Local),
            TEST_CONSTANTS.TEST_FOLDER,
            True,
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
            file_storage(provider=FileStorageProvider.Local),
            TEST_CONSTANTS.TEST_FOLDER,
            True,
        ),
        (
            file_storage(provider=FileStorageProvider.Local),
            "dummy",
            False,
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
            file_storage(provider=FileStorageProvider.Local),
            TEST_CONSTANTS.READ_FOLDER_PATH,
            3,
        ),
        (
            file_storage(provider=FileStorageProvider.Local),
            TEST_CONSTANTS.READ_TEXT_FILE,
            1,
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
            file_storage(provider=FileStorageProvider.Local),
            TEST_CONSTANTS.WRITE_FOLDER_PATH,
        ),
    ],
)
def test_rm(file_storage, folder_path):
    if not file_storage.exists(path=folder_path):
        file_storage.mkdir(path=folder_path)
    file_storage.rm(path=folder_path)
    assert file_storage.exists(path=folder_path) == False  # noqa


@pytest.mark.parametrize(
    "file_storage, folder_path, recursive, test_folder_path",
    [
        (
            file_storage(provider=FileStorageProvider.Local),
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
            file_storage(provider=FileStorageProvider.Local),
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
            file_storage(provider=FileStorageProvider.Local),
            TEST_CONSTANTS.READ_TEXT_FILE,
            "rb",
            1,
            0,
            os.path.getsize(TEST_CONSTANTS.READ_TEXT_FILE) - 1,
        ),
        (
            file_storage(provider=FileStorageProvider.Local),
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
    with pytest.raises(FileStorageError):
        FileStorage(provider=provider)
    load_dotenv()


@pytest.mark.parametrize(
    "file_storage, lpath, rpath",
    [
        (
            file_storage(provider=FileStorageProvider.GCS),
            TEST_CONSTANTS.READ_TEXT_FILE,
            TEST_CONSTANTS.TEST_FOLDER,
        ),
        (
            file_storage(provider=FileStorageProvider.Local),
            TEST_CONSTANTS.READ_TEXT_FILE,
            TEST_CONSTANTS.TEST_FOLDER,
        ),
    ],
)
def test_cp(file_storage, lpath, rpath):
    file_storage.cp(lpath, rpath)
    assert file_storage.exists(rpath) is True
    file_storage.rm(rpath, recursive=True)
    assert file_storage.exists(rpath) is False


def test_pdf_read():
    fs = file_storage(FileStorageProvider.Local)
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
            file_storage(provider=FileStorageProvider.Local),
            TEST_CONSTANTS.READ_TEXT_FILE,
            os.path.getsize(TEST_CONSTANTS.READ_TEXT_FILE),
        ),
    ],
)
def test_file_size(file_storage, path, expected_size):
    file_size = file_storage.size(path=path)
    assert file_size == expected_size


@pytest.mark.parametrize(
    "file_storage, file_read_path, read_mode, file_write_path, write_mode",
    [
        (
            permanent_file_storage(provider=FileStorageProvider.GCS),
            "fsspec-test/input/3.txt",
            "r",
            "fsspec-test/output/copy_on_write.txt",
            "w",
        )
    ],
)
def test_permanent_fs_copy_on_write(
    file_storage, file_read_path, read_mode, file_write_path, write_mode
):
    if file_storage.exists(file_read_path):
        file_storage.rm(file_read_path)
    file_read_contents = file_storage.read(file_read_path, read_mode)
    print(file_read_contents)
    file_storage.write(file_write_path, write_mode, data=file_read_contents)

    file_write_contents = file_storage.read(file_write_path, read_mode)
    assert len(file_read_contents) == len(file_write_contents)


@pytest.mark.parametrize(
    "provider",
    [(FileStorageProvider.GCS)],
)
def test_permanent_supported_file_storage_mode(provider):
    file_storage = permanent_file_storage(provider=provider)
    assert file_storage is not None and isinstance(file_storage, PermanentFileStorage)
