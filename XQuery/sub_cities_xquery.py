from BaseXClient import BaseXClient
import lxml.etree as etree

def filter_brazilian_cities(xquery_file, output_file):
    with open(xquery_file, 'r') as file:
        xquery = file.read()
    session = BaseXClient.Session('localhost', 1984, 'admin', '1234')
    try:
        result = session.query(xquery).execute()
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"Output written to {output_file}")
    finally:
        session.close()

def validate_xml(xml_file, xsd_file):
    with open(xsd_file, 'rb') as schema_file: 
        schema_root = etree.XML(schema_file.read())
        schema = etree.XMLSchema(schema_root)
        xml_parser = etree.XMLParser(schema=schema)
        try:
            with open(xml_file, 'rb') as xml:
                etree.fromstring(xml.read(), xml_parser)
            print("XML is valid.")
        except etree.XMLSyntaxError as e:
            print("XML is invalid:", e)

if __name__ == "__main__":
    xquery_file = "filter_brazilian_cities.xquery"
    output_file = "brazilian_cities.xml"
    filter_brazilian_cities(xquery_file, output_file)
    validate_xml("new_cities.xml", "schema.xsd")