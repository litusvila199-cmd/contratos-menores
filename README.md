# Contratos Menores - Data Downloader

Python project for the automated download and extraction of public procurement
data published by the Spanish Public Procurement Platform.

The project downloads the source data in ZIP format, keeps the original ZIP
files, and extracts them to obtain the corresponding `.atom` files.

## Objective

The main objective of this project is to automate the download of historical
and current public procurement data while avoiding the re-download of files
that are already available locally.

The process is designed to be executed periodically and detect new files as
they become available.

## How It Works

The downloader follows these steps:

1. Identifies the current year and month.
2. Downloads historical data using annual ZIP files.
3. Downloads current-year data using monthly ZIP files.
4. Checks whether each file is already available locally.
5. Checks whether the requested file is available on the remote server.
6. Downloads available ZIP files in chunks.
7. Extracts the downloaded ZIP files.
8. Logs the different steps and possible errors.

Existing files are skipped to avoid unnecessary downloads.

## Project Structure

```text
contratos-menores/
│
├── data/
│
├── src/
│   ├── __init__.py
│   ├── download_data.py
│   └── logger.py
│
├── tests/
│   └── test_download_data.py
│
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md


