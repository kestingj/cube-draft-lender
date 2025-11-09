import sys
import os
import glob
import time

import xml.etree.ElementTree as ET

from file_helpers import get_draft_dir, get_owned_path, get_downloads_folder

def parse_dek_file(filename):
    """
    Reads a .dek file and returns a mapping of card card_name to CatId.
    """
    tree = ET.parse(filename)
    root = tree.getroot()
    card_map = {}
    for card in root.findall('Cards'):
        card_name = card.attrib.get('Name')
        catid = card.attrib.get('CatID')
        if card_name and catid:
            card_map[card_name] = catid
    return card_map

def generate_dek_file(card_map, dek_file_path):
    import xml.etree.ElementTree as ET

    deck = ET.Element("Deck", {
        "xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance"
    })
    ET.SubElement(deck, "NetDeckID").text = "0"
    ET.SubElement(deck, "PreconstructedDeckID").text = "0"
    
    for card_name, item_id in card_map.items():
        card = ET.SubElement(deck, "Cards")
        card.set("CatID", str(item_id))
        card.set("Quantity", "1")
        card.set("Sideboard", "false")
        card.set("Name", card_name)
        card.set("Annotation", "0")
        # Add a newline after each card element for readability

    tree = ET.ElementTree(deck)
    ET.indent(tree, '  ')
    tree.write(dek_file_path, encoding="utf-8", xml_declaration=True)
    print(f".dek file created at: {dek_file_path}")

# Example usage:
# card_mapping = parse_dek_file('your_file.dek')
def main():
    if len(sys.argv) != 2:
        print("Usage: python create-trade-binders.py <draft_name>")
        return
    draft_name = sys.argv[1]
    draft_dir = get_draft_dir(draft_name)
    owned_card_mapping = parse_dek_file(get_owned_path())
    downloads_folder = get_downloads_folder()
    now = time.time()
    dek_files = glob.glob(os.path.join(downloads_folder, "*.dek"))
    # recent_dek_files = [f for f in dek_files if now - os.path.getmtime(f) < 120]
    recent_dek_files = [f for f in dek_files]

    if not recent_dek_files:
        print("No recent .dek file found in Downloads folder.")
        return

    # Use the most recently modified .dek file
    recent_dek_file = max(recent_dek_files, key=os.path.getmtime)
    print(f"Using rented .dek file: {recent_dek_file}")
    rented_card_mapping = parse_dek_file(recent_dek_file)
    print(f"RENTED items: {rented_card_mapping}")
    card_mapping = {**owned_card_mapping, **rented_card_mapping}
    txt_files = [f for f in os.listdir(draft_dir) if f.endswith('.txt')]
    list_card_mappings = {}

    for txt_file in txt_files:
        card_names = []
        with open(os.path.join(draft_dir, txt_file), "r", encoding="utf-8") as f:
            drafted_card = []
            for line in f:
                card = line.strip()
                if card.startswith("1 "):
                    card = card[2:]
                if card == "Fire":
                    card = "Fire // Ice"
                drafted_card.append(card)
            card_names.extend(drafted_card)
        filtered_mapping = {}
        for card_name in card_names:
            if card_name in card_mapping:
                filtered_mapping[card_name] = card_mapping[card_name]
                continue

            # Additional matching rules for split cards
            matched = False
            if "/" in card_name or "//" in card_name:
                # Try matching before the first slash
                base_name = card_name.split("/")[0].strip()
                if base_name in card_mapping:
                    filtered_mapping[card_name] = card_mapping[base_name]
                    matched = True
                # Try matching with " // " replaced by "/"
                alt_name = card_name.replace(" // ", "/")
                if not matched and alt_name in card_mapping:
                    filtered_mapping[card_name] = card_mapping[alt_name]
                    matched = True

            if not matched:
                print(f"Error: '{card_name}' not found in card_mapping")
        dek_file_path = txt_file.rsplit('.', 1)[0] + '_trade_binder.dek'
        generate_dek_file(filtered_mapping, os.path.join(draft_name, dek_file_path))
        list_card_mappings[txt_file] = filtered_mapping

    print(list_card_mappings)
    print(card_mapping)

if __name__ == "__main__":
    main()