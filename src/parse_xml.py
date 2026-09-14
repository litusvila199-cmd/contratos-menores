import csv
import xml.etree.ElementTree as ET
from pathlib import Path

from src.logger import logger


DATA_DIR = Path("data/2025")
OUTPUT_FILE = DATA_DIR / "contacts_2025.csv"


def get_text(element, tag_name):
    """Finds the first element with the given tag and returns its text."""

    if element is None:
        return None

    for child in element.iter():
        if child.tag.endswith(tag_name):
            if child.text and child.text.strip():
                return child.text.strip()

    return None


def extract_entry(entry):
    """Extracts location and contact information from one entry."""

    contract_folder_status = None

    for child in entry:
        if child.tag.endswith("ContractFolderStatus"):
            contract_folder_status = child
            break

    if contract_folder_status is None:
        return None

    located_party = None

    for child in contract_folder_status:
        if child.tag.endswith("LocatedContractingParty"):
            located_party = child
            break

    if located_party is None:
        return None

    party = None

    for child in located_party:
        if child.tag.endswith("Party"):
            party = child
            break

    if party is None:
        return None

    postal_address = None

    for child in party:
        if child.tag.endswith("PostalAddress"):
            postal_address = child
            break

    contact = None

    for child in party:
        if child.tag.endswith("Contact"):
            contact = child
            break

    city = get_text(postal_address, "CityName")
    postal_code = get_text(postal_address, "PostalZone")
    address = get_text(postal_address, "Line")

    contact_name = get_text(contact, "Name")
    telephone = get_text(contact, "Telephone")
    email = get_text(contact, "ElectronicMail")

    return {
        "city": city,
        "postal_code": postal_code,
        "address": address,
        "contact_name": contact_name,
        "telephone": telephone,
        "email": email,
    }


def parse_atom_file(atom_file):
    """Parses one Atom file."""

    records = []

    try:
        tree = ET.parse(atom_file)
        root = tree.getroot()

        for child in root:

            if child.tag.endswith("entry"):

                record = extract_entry(child)

                if record is not None:
                    records.append(record)

    except ET.ParseError as error:
        logger.error(
            "XML error in %s: %s",
            atom_file.name,
            error
        )

    except OSError as error:
        logger.error(
            "File error in %s: %s",
            atom_file.name,
            error
        )

    return records


def main():
    """Parses all Atom files from 2025."""

    atom_files = sorted(DATA_DIR.rglob("*.atom"))

    logger.info(
        "Found %s Atom files",
        len(atom_files)
    )

    all_records = []

    for atom_file in atom_files:

        logger.info(
            "Processing: %s",
            atom_file.name
        )

        records = parse_atom_file(atom_file)

        all_records.extend(records)

    fieldnames = [
        "city",
        "postal_code",
        "address",
        "contact_name",
        "telephone",
        "email",
    ]

    try:
        with open(
            OUTPUT_FILE,
            "w",
            newline="",
            encoding="utf-8"
        ) as csv_file:

            writer = csv.DictWriter(
                csv_file,
                fieldnames=fieldnames
            )

            writer.writeheader()
            writer.writerows(all_records)

        logger.info(
            "Records extracted: %s",
            len(all_records)
        )

        logger.info(
            "Output file: %s",
            OUTPUT_FILE
        )

    except OSError as error:
        logger.error(
            "Error writing CSV: %s",
            error
        )


if __name__ == "__main__":
    main()