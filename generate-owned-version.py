import csv
import sys

def read_name_to_itemid_map(csv_file_path):
    name_to_itemid = {}
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = row.get('name')
            item_id = row.get('itemID')
            if name and item_id and name != 'Event Ticket':
                name_to_itemid[name] = item_id

    print(f"items: {name_to_itemid}")
    return name_to_itemid

def generate_dek_file(card_map, dek_file_path):
    import xml.etree.ElementTree as ET

    deck = ET.Element("Deck", {
        "xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance"
    })
    ET.SubElement(deck, "NetDeckID").text = "0"
    ET.SubElement(deck, "PreconstructedDeckID").text = "0"
    
    for name, item_id in card_map.items():
        card = ET.SubElement(deck, "Cards")
        card.set("CatID", str(item_id))
        card.set("Quantity", "1")
        card.set("Sideboard", "false")
        card.set("Name", name)
        card.set("Annotation", "0")
        # Add a newline after each card element for readability

    tree = ET.ElementTree(deck)
    ET.indent(tree, '  ')
    tree.write(dek_file_path, encoding="utf-8", xml_declaration=True)
    print(f"Number of cards in deck: {len(card_map)}")
    print(f".dek file created at: {dek_file_path}")

# Example usage:
# csv_map = read_name_to_itemid_map('your_file.csv')
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <csv_file_path>")
        sys.exit(1)
    csv_file_path = sys.argv[1]
    csv_map = read_name_to_itemid_map(csv_file_path)

    dek_file_path = csv_file_path.rsplit('.', 1)[0] + '.dek'
    generate_dek_file(csv_map, dek_file_path)

    
