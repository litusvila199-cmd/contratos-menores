from datetime import datetime
from pathlib import Path
import zipfile

import requests

from src.logger import logger


BASE_URL = (
    "https://contrataciondelestado.es/"
    "sindicacion/sindicacion_1143"
)

START_YEAR = 2018


def get_current_year_month():
    """Returns the current year and month."""
    now = datetime.now()
    return now.year, now.month


def build_monthly_file_info(year, month):
    """Builds the URL and local path for the monthly ZIP file."""
    month_str = f"{month:02d}"

    file_name = (
        f"contratosMenoresPerfilesContratantes_"
        f"{year}{month_str}.zip"
    )

    url = f"{BASE_URL}/{file_name}"

    output_path = (
        Path("data")
        / str(year)
        / month_str
        / file_name
    )

    return url, output_path


def build_annual_file_info(year):
    """Builds the URL and local path for the annual ZIP file."""
    file_name = (
        f"contratosMenoresPerfilesContratantes_"
        f"{year}.zip"
    )

    url = f"{BASE_URL}/{file_name}"

    output_path = Path("data") / str(year) / file_name

    return url, output_path


def remote_file_exists(url):
    """Checks whether a file exists without downloading it completely."""
    try:
        response = requests.get(
            url,
            stream=True,
            timeout=30
        )

        if response.status_code == 404:
            response.close()
            return False

        response.raise_for_status()
        response.close()

        return True

    except requests.RequestException as error:
        logger.error(
            "Error checking %s: %s",
            url,
            error
        )
        return False


def download_file(url, output_path):
    """Downloads a ZIP file in chunks."""
    logger.info(
        "Downloading file: %s",
        output_path.name
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    try:
        response = requests.get(
            url,
            stream=True,
            timeout=60
        )

        response.raise_for_status()

        with open(output_path, "wb") as file:
            for chunk in response.iter_content(
                chunk_size=8192
            ):
                if chunk:
                    file.write(chunk)

        response.close()

        logger.info(
            "File downloaded successfully: %s",
            output_path.name
        )

        return True

    except requests.RequestException as error:
        logger.error(
            "Error downloading %s: %s",
            output_path.name,
            error
        )
        return False

    except OSError as error:
        logger.error(
            "Error saving %s: %s",
            output_path.name,
            error
        )
        return False


def extract_file(zip_path):
    """Extracts a ZIP file into its directory."""
    logger.info(
        "Extracting file: %s",
        zip_path.name
    )

    try:
        with zipfile.ZipFile(zip_path, "r") as zip_file:
            zip_file.extractall(zip_path.parent)

        logger.info(
            "File extracted successfully: %s",
            zip_path.name
        )

        return True

    except zipfile.BadZipFile:
        logger.error(
            "The file is not a valid ZIP: %s",
            zip_path.name
        )
        return False

    except OSError as error:
        logger.error(
            "Error extracting %s: %s",
            zip_path.name,
            error
        )
        return False


def process_file(url, output_path):
    """Downloads and extracts a file if it does not already exist."""
    if output_path.exists():
        logger.info(
            "File already exists, skipping: %s",
            output_path.name
        )
        return True

    if not remote_file_exists(url):
        logger.info(
            "File is not available: %s",
            output_path.name
        )
        return False

    if not download_file(url, output_path):
        return False

    return extract_file(output_path)


def process_annual_file(year):
    """Processes the annual file for a historical year."""
    url, output_path = build_annual_file_info(year)

    logger.info(
        "Processing annual data for %s",
        year
    )

    process_file(url, output_path)


def process_current_year(year, current_month):
    """Processes the monthly files for the current year."""
    logger.info(
        "Processing monthly data for %s",
        year
    )

    for month in range(1, current_month + 1):
        url, output_path = build_monthly_file_info(
            year,
            month
        )

        if output_path.exists():
            logger.info(
                "File already exists, skipping: %s",
                output_path.name
            )
            continue

        if not remote_file_exists(url):
            logger.info(
                "Monthly file is not available yet: %s",
                output_path.name
            )
            continue

        process_file(
            url,
            output_path
        )


def main():
    """Runs the complete download process."""
    logger.info("Starting download process")

    current_year, current_month = get_current_year_month()

    for year in range(START_YEAR, current_year):
        process_annual_file(year)

    process_current_year(
        current_year,
        current_month
    )

    logger.info("Download process finished")


if __name__ == "__main__":
    main()