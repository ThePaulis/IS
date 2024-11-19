from xml.dom import minidom

# Carrega o ficheiro xml e da parse ao mesmo
try:
    xml_doc = minidom.parse('ebay.xml')
except Exception as e:
    print(f"Error parsing XML: {e}")
    exit()

# Da print ao nome da tag raiz do ficheiro xml
root = xml_doc.documentElement
print(f"Root tag: {root.tagName}")

# Itera sobre todas as listagens
listings = root.getElementsByTagName('listing')
for listing in listings:
    # Extrai as informações do vendedor
    seller_name = listing.getElementsByTagName('seller_name')[0].firstChild.data.strip()
    seller_rating = listing.getElementsByTagName('seller_rating')[0].firstChild.data.strip()

    # Extrai as informações da licitagem
    current_bid = listing.getElementsByTagName('current_bid')[0].firstChild.data.strip()
    high_bidder = listing.getElementsByTagName('bidder_name')[0].firstChild.data.strip()
    
    # Extrai as informações do produto
    memory = listing.getElementsByTagName('memory')[0].firstChild.data.strip()
    cpu = listing.getElementsByTagName('cpu')[0].firstChild.data.strip()
    
    # Faz display das informações
    print(f"Seller: {seller_name} (Rating: {seller_rating})")
    print(f"Current Bid: {current_bid}, High Bidder: {high_bidder}")
    print(f"Memory: {memory}, CPU: {cpu}")
    print("-" * 40)
