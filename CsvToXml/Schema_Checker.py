from lxml import etree

def validate_xml(xml_file, xsd_file):
    with open(xsd_file, 'rb') as schema_file:  # Abrir como bytes
        schema_root = etree.XML(schema_file.read())
        schema = etree.XMLSchema(schema_root)
        xml_parser = etree.XMLParser(schema=schema)
        
        try:
            with open(xml_file, 'rb') as xml:  # Abrir como bytes
                etree.fromstring(xml.read(), xml_parser)
            print("XML is valid.")
        except etree.XMLSyntaxError as e:
            print("XML is invalid:", e)

if __name__ == "__main__":
    validate_xml("cities.xml", "schema.xsd")