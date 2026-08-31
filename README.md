# Contratos Menores - Data Downloader

Proyecto para la descarga y descompresión automatizada de los datos de
contratos menores publicados por la Plataforma de Contratación del Sector
Público.

El proyecto descarga los archivos en formato ZIP, los conserva como fuente
original y posteriormente los descomprime para obtener los archivos `.atom`.

## Objetivo

Automatizar la descarga de los datos históricos y actuales de contratos
menores, evitando descargar nuevamente archivos que ya existen localmente.

El proceso está preparado para poder ejecutarse periódicamente y detectar
nuevos archivos disponibles.

## Estructura del proyecto

```text
contratos-menores/
├── data/
├── src/
│   ├── __init__.py
│   ├── download_data.py
│   └── logger.py
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md