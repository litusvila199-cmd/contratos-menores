import xml.etree.ElementTree as ET

from src.parse_xml import get_text, parse_entry


def create_entry():
    """Creates a test XML entry."""
    xml = """
    <entry xmlns="http://www.w3.org/2005/Atom"
           xmlns:cbc="urn:dgpe:names:draft:codice:schema:xsd:CommonBasicComponents-2"
           xmlns:cac="urn:dgpe:names:draft:codice:schema:xsd:CommonAggregateComponents-2"
           xmlns:cac-place-ext="urn:dgpe:names:draft:codice-place-ext:schema:xsd:CommonAggregateComponents-2">

        <link href="https://example.com/contract"></link>

        <cac-place-ext:ContractFolderStatus>

            <cbc:ContractFolderID>123/2025</cbc:ContractFolderID>

            <cac-place-ext:LocatedContractingParty>
                <cac:Party>

                    <cac:PartyName>
                        <cbc:Name>Ayuntamiento de Murcia</cbc:Name>
                    </cac:PartyName>

                    <cac:Contact>
                        <cbc:ElectronicMail>
                            test@example.com
                        </cbc:ElectronicMail>
                    </cac:Contact>

                </cac:Party>
            </cac-place-ext:LocatedContractingParty>

            <cac:TenderResult>
                <cac:WinningParty>
                    <cac:PartyName>
                        <cbc:Name>Empresa de Prueba S.L.</cbc:Name>
                    </cac:PartyName>
                </cac:WinningParty>
            </cac:TenderResult>

        </cac-place-ext:ContractFolderStatus>
    </entry>
    """

    return ET.fromstring(xml)


def test_parse_entry():
    """Tests extraction of all contract fields."""
    entry = create_entry()

    result = parse_entry(entry)

    assert result["contract_id"] == "123/2025"
    assert result["contracting_party"] == "Ayuntamiento de Murcia"
    assert result["email"] == "test@example.com"
    assert result["winning_party"] == "Empresa de Prueba S.L."
    assert result["url"] == "https://example.com/contract"


def test_get_text_with_missing_element():
    """Tests that missing XML elements return an empty string."""
    entry = create_entry()

    result = get_text(
        entry,
        "cbc:DoesNotExist"
    )

    assert result == ""


def test_get_text_with_none_element():
    """Tests that a None element returns an empty string."""
    result = get_text(
        None,
        "cbc:ContractFolderID"
    )

    assert result == ""


def test_parse_entry_without_contract_status():
    """Tests an entry without ContractFolderStatus."""
    xml = """
    <entry xmlns="http://www.w3.org/2005/Atom">
        <link href="https://example.com/contract"></link>
    </entry>
    """

    entry = ET.fromstring(xml)

    result = parse_entry(entry)

    assert result is None