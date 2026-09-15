import csv
import xml.etree.ElementTree as ET
from pathlib import Path

from src.logger import logger


NAMESPACES = {
    "cbc": "urn:dgpe:names:draft:codice:schema:xsd:CommonBasicComponents-2",
    "cac": "urn:dgpe:names:draft:codice:schema:xsd:CommonAggregateComponents-2",
    "cac-place-ext": (
        "urn:dgpe:names:draft:codice-place-ext:"
        "schema:xsd:CommonAggregateComponents-2"
    ),
}


def get_text(element, path):
    """Returns the text of an XML element."""
    if element is None:
        return ""
    
    try:
        child = element.find(path, NAMESPACES)

        if child is None or child.text is None:
            return ""

        return child.text.strip()

    except AttributeError as error:
        logger.error("Error extracting XML field: %s", error)
        return ""


def parse_entry(entry):
    """Extracts the required fields from a contract."""
    contract_status = entry.find(
        "cac-place-ext:ContractFolderStatus",
        NAMESPACES
    )

    if contract_status is None:
        logger.warning("ContractFolderStatus not found")
        return None

    party = contract_status.find(
        "cac-place-ext:LocatedContractingParty/cac:Party",
        NAMESPACES
    )

    contact = contract_status.find(
        "cac-place-ext:LocatedContractingParty/cac:Party/cac:Contact",
        NAMESPACES
    )

    tender_result = contract_status.find(
        "cac:TenderResult",
        NAMESPACES
    )

    return {
        "contract_id": get_text(
            contract_status,
            "cbc:ContractFolderID"
        ),
        "contracting_party": get_text(
            party,
            "cac:PartyName/cbc:Name"
        ),
        "email": get_text(
            contact,
            "cbc:ElectronicMail"
        ),
        "winning_party": get_text(
            tender_result,
            "cac:WinningParty/cac:PartyName/cbc:Name"
        ),
        "url": entry.find(
            "{http://www.w3.org/2005/Atom}link"
        ).get("href", ""),
    }


def process_year(year):
    """Processes all XML files of a year and creates a CSV."""
    year_path = Path("data") / str(year)
    records = []

    for xml_file in year_path.rglob("*.atom"):
        try:
            root = ET.parse(xml_file).getroot()

            for entry in root.findall(
                "{http://www.w3.org/2005/Atom}entry"
            ):
                record = parse_entry(entry)

                if record:
                    records.append(record)

        except ET.ParseError as error:
            logger.error(
                "Error parsing %s: %s",
                xml_file.name,
                error
            )

        except OSError as error:
            logger.error(
                "Error reading %s: %s",
                xml_file.name,
                error
            )

    output_file = year_path / f"contracts_{year}.csv"

    with open(output_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "contract_id",
                "contracting_party",
                "email",
                "winning_party",
                "url",
            ],
        )

        writer.writeheader()
        writer.writerows(records)

    logger.info(
        "Year %s processed: %s records",
        year,
        len(records)
    )


def main():
    """Processes all available years."""
    logger.info("Starting XML parsing process")

    for year_path in sorted(Path("data").iterdir()):
        if year_path.is_dir() and year_path.name.isdigit():
            process_year(int(year_path.name))

    logger.info("XML parsing process finished")


if __name__ == "__main__":
    main()



    