import xml.etree.ElementTree as ET
import os

class Binder:
    def __init__(self, name: str, cards: dict):
        self.name = name
        self.cards = cards

    def card_names(self):   
        return self.cards.keys()

    def get_subset(self, card_names: list[str], subset_name) -> "Binder":
        filtered_mapping = {}
        for card_name in card_names:
            if card_name in self.cards:
                filtered_mapping[card_name] = self.cards[card_name]
                continue

            # Additional matching rules for split cards
            matched = False
            if "/" in card_name or "//" in card_name:
                # Try matching before the first slash
                base_name = card_name.split("/")[0].strip()
                if base_name in self.cards:
                    filtered_mapping[card_name] = self.cards[base_name]
                    matched = True
                # Try matching with " // " replaced by "/"
                alt_name = card_name.replace(" // ", "/")
                if not matched and alt_name in self.cards:
                    filtered_mapping[card_name] = self.cards[alt_name]
                    matched = True

            if not matched:
                print(f"Error: '{card_name}' not found in self.cards")
        return Binder(subset_name, filtered_mapping)

    def write_to_file(self, file_path):
        deck = ET.Element("Deck", {
            "xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance"
        })
        ET.SubElement(deck, "NetDeckID").text = "0"
        ET.SubElement(deck, "PreconstructedDeckID").text = "0"
        
        for card_name, item_id in self.cards.items():
            card = ET.SubElement(deck, "Cards")
            card.set("CatID", str(item_id))
            card.set("Quantity", "1")
            card.set("Sideboard", "false")
            card.set("Name", card_name)
            card.set("Annotation", "0")
            # Add a newline after each card element for readability

        tree = ET.ElementTree(deck)
        ET.indent(tree, '  ')
        tree.write(file_path, encoding="utf-8", xml_declaration=True)
        print(f".dek file created at: {file_path}")

@staticmethod
def combine_binders(b1: Binder, b2: Binder) -> "Binder":
    """
    Return a new Binder that is the combination of b1 and b2.
    Raises ValueError if a card name exists in both binders.
    """
    merged = dict(b1.cards)
    for name, catid in b2.cards.items():
        if name in merged and merged[name] != catid:
            raise ValueError(f"Conflict for card '{name}' between binders '{b1.name}' and '{b2.name}'")
        merged[name] = catid

    new_name = f"{b1.name}+{b2.name}"
    return Binder(new_name, merged)
    

def from_dek_file(filename) -> "Binder":
    card_map = parse_dek_file(filename)
    binder_name = os.path.splitext(os.path.basename(filename))[0]
    return Binder(binder_name, card_map)

def parse_dek_file(filename):
    """
    Reads a .dek file and returns a mapping of card name to CatId.
    """
    tree = ET.parse(filename)
    root = tree.getroot()
    card_map = {}
    for card in root.findall('Cards'):
        card_name = normalize_name(card.attrib.get('Name'))
        catid = card.attrib.get('CatID')
        if card_name in card_map:
            print(f"Warning: Duplicate card name '{card_name}' found in {filename} (existing CatID: {card_map[card_name]}, new CatID: {catid})")
        if card_name and catid:
            card_map[card_name] = catid
        else: print(f"Warning: Missing Name or CatID in card element: {ET.tostring(card, encoding='unicode')}")
    return card_map

def from_txt_file(filename) -> list[str]:
    """
    Reads a .txt file and returns a list of card names.
    """
    card_names = []
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            card = line.strip()
            # Remove "1 " prefix and handle special cases
            if card.startswith("1 "):
                card = card[2:]
            # Remove empty lines
            if card.strip():
                card_names.append(normalize_name(card))

    return card_names

def normalize_name(card_name):
    return card_name.lower().replace("&", "and").strip()
