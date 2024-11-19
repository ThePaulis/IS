from lxml import etree

def transform_xml(xml_file, xsl_file, output_file):
    dom = etree.parse(xml_file)
    xslt = etree.parse(xsl_file)
    transform = etree.XSLT(xslt)
    new_dom = transform(dom)
    
    with open(output_file, 'wb') as f:
        f.write(etree.tostring(new_dom, pretty_print=True))


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
    transform_xml("cities.xml", "sub_xml.xsl", "new_cities.xml")
    validate_xml("new_cities.xml", "schema.xsd")