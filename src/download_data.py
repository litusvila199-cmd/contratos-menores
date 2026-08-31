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
    """Devuelve el año y el mes actuales."""
    now = datetime.now()
    return now.year, now.month


def build_monthly_file_info(year, month):
    """Construye la URL y la ruta local del ZIP mensual."""
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
    """Construye la URL y la ruta local del ZIP anual."""
    file_name = (
        f"contratosMenoresPerfilesContratantes_"
        f"{year}.zip"
    )

    url = f"{BASE_URL}/{file_name}"

    output_path = Path("data") / str(year) / file_name

    return url, output_path


def remote_file_exists(url):
    """Comprueba si un fichero existe sin descargarlo completo."""
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
            "Error comprobando %s: %s",
            url,
            error
        )
        return False


def download_file(url, output_path):
    """Descarga un archivo ZIP por bloques."""
    logger.info(
        "Descargando archivo: %s",
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
            "Archivo descargado correctamente: %s",
            output_path.name
        )

        return True

    except requests.RequestException as error:
        logger.error(
            "Error al descargar %s: %s",
            output_path.name,
            error
        )
        return False

    except OSError as error:
        logger.error(
            "Error guardando %s: %s",
            output_path.name,
            error
        )
        return False


def extract_file(zip_path):
    """Descomprime un archivo ZIP en su directorio."""
    logger.info(
        "Descomprimiendo archivo: %s",
        zip_path.name
    )

    try:
        with zipfile.ZipFile(zip_path, "r") as zip_file:
            zip_file.extractall(zip_path.parent)

        logger.info(
            "Archivo descomprimido correctamente: %s",
            zip_path.name
        )

        return True

    except zipfile.BadZipFile:
        logger.error(
            "El archivo no es un ZIP válido: %s",
            zip_path.name
        )
        return False

    except OSError as error:
        logger.error(
            "Error al descomprimir %s: %s",
            zip_path.name,
            error
        )
        return False


def process_file(url, output_path):
    """Descarga y descomprime un fichero si aún no existe."""
    if output_path.exists():
        logger.info(
            "El archivo ya existe, se omite: %s",
            output_path.name
        )
        return True

    if not remote_file_exists(url):
        logger.info(
            "El archivo no está disponible: %s",
            output_path.name
        )
        return False

    if not download_file(url, output_path):
        return False

    return extract_file(output_path)


def process_annual_file(year):
    """Procesa el archivo anual de un año histórico."""
    url, output_path = build_annual_file_info(year)

    logger.info(
        "Procesando datos anuales de %s",
        year
    )

    process_file(url, output_path)


def process_current_year(year, current_month):
    """Procesa los archivos mensuales del año actual."""
    logger.info(
        "Procesando datos mensuales de %s",
        year
    )

    for month in range(1, current_month + 1):
        url, output_path = build_monthly_file_info(
            year,
            month
        )

        if output_path.exists():
            logger.info(
                "El archivo ya existe, se omite: %s",
                output_path.name
            )
            continue

        if not remote_file_exists(url):
            logger.info(
                "El archivo mensual todavía no está disponible: %s",
                output_path.name
            )
            continue

        process_file(
            url,
            output_path
        )


def main():
    """Ejecuta el proceso completo de descarga."""
    logger.info("Iniciando proceso de descarga")

    current_year, current_month = get_current_year_month()

    for year in range(START_YEAR, current_year):
        process_annual_file(year)

    process_current_year(
        current_year,
        current_month
    )

    logger.info("Proceso de descarga finalizado")


if __name__ == "__main__":
    main()
