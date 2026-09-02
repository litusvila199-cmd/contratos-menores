from pathlib import Path
import zipfile

from src import download_data


def test_build_monthly_file_info():
    url, output_path = download_data.build_monthly_file_info(2026, 8)

    assert url.endswith(
        "contratosMenoresPerfilesContratantes_202608.zip"
    )

    assert str(output_path).endswith(
        "data/2026/08/"
        "contratosMenoresPerfilesContratantes_202608.zip"
    )


def test_build_annual_file_info():
    url, output_path = download_data.build_annual_file_info(2025)

    assert url.endswith(
        "contratosMenoresPerfilesContratantes_2025.zip"
    )

    assert str(output_path).endswith(
        "data/2025/"
        "contratosMenoresPerfilesContratantes_2025.zip"
    )


def test_remote_file_exists(monkeypatch):
    class MockResponse:
        status_code = 200

        def close(self):
            pass

        def raise_for_status(self):
            pass

    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(
        download_data.requests,
        "get",
        mock_get
    )

    result = download_data.remote_file_exists(
        "https://example.com/file.zip"
    )

    assert result is True


def test_remote_file_does_not_exist(monkeypatch):
    class MockResponse:
        status_code = 404

        def close(self):
            pass

    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(
        download_data.requests,
        "get",
        mock_get
    )

    result = download_data.remote_file_exists(
        "https://example.com/file.zip"
    )

    assert result is False


def test_download_file(tmp_path, monkeypatch):
    class MockResponse:
        def iter_content(self, chunk_size):
            return [
                b"hello ",
                b"world"
            ]

        def raise_for_status(self):
            pass

        def close(self):
            pass

    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(
        download_data.requests,
        "get",
        mock_get
    )

    output_path = tmp_path / "test.zip"

    result = download_data.download_file(
        "https://example.com/test.zip",
        output_path
    )

    assert result is True
    assert output_path.exists()
    assert output_path.read_bytes() == b"hello world"


def test_extract_file(tmp_path):
    zip_path = tmp_path / "test.zip"

    file_inside_zip = tmp_path / "test.txt"
    file_inside_zip.write_text("hello")

    with zipfile.ZipFile(zip_path, "w") as zip_file:
        zip_file.write(
            file_inside_zip,
            arcname="test.txt"
        )

    file_inside_zip.unlink()

    result = download_data.extract_file(zip_path)

    assert result is True
    assert (tmp_path / "test.txt").exists()
    assert (tmp_path / "test.txt").read_text() == "hello"


def test_extract_invalid_zip(tmp_path):
    zip_path = tmp_path / "invalid.zip"
    zip_path.write_text("this is not a zip file")

    result = download_data.extract_file(zip_path)

    assert result is False


def test_process_file_skips_existing_file(tmp_path, monkeypatch):
    output_path = tmp_path / "existing.zip"
    output_path.write_text("already exists")

    def fail_if_called(*args, **kwargs):
        raise AssertionError(
            "The file should not be downloaded"
        )

    monkeypatch.setattr(
        download_data,
        "remote_file_exists",
        fail_if_called
    )

    result = download_data.process_file(
        "https://example.com/existing.zip",
        output_path
    )

    assert result is True


def test_process_file(monkeypatch, tmp_path):
    output_path = tmp_path / "test.zip"

    monkeypatch.setattr(
        download_data,
        "remote_file_exists",
        lambda url: True
    )

    monkeypatch.setattr(
        download_data,
        "download_file",
        lambda url, path: True
    )

    monkeypatch.setattr(
        download_data,
        "extract_file",
        lambda path: True
    )

    result = download_data.process_file(
        "https://example.com/test.zip",
        output_path
    )

    assert result is True