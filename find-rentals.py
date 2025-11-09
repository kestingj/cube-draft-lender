import glob
import os
import sys
import xml.etree.ElementTree as ET
from file_helpers import get_draft_dir, get_owned_path

def main():

    if len(sys.argv) != 2:
        print("Usage: python find-rentals.py <name>")
        sys.exit(1)

    name = sys.argv[1]
    draft_dir = get_draft_dir(name)
    # rentals_path = "C:/Users/Joseph Kesting/Documents/DiscordDrafts/rentals.txt"
    rentals_path = os.path.join(draft_dir, "rentals.txt")

    # Copy .dektxt files that start with Session_<name>_Deck from Downloads to draft_dir
    downloads_dir = os.path.expanduser(r"~/Downloads")
    pattern = f"Session_{name}_Deck*.txt"
    dest_dir = draft_dir
    os.makedirs(dest_dir, exist_ok=True)
    for file_path in glob.glob(os.path.join(downloads_dir, pattern)):
        dest_path = os.path.join(dest_dir, os.path.basename(file_path))
        with open(file_path, "rb") as src, open(dest_path, "wb") as dst:
            dst.write(src.read())
    
    # Read all .dektxt files from draft_dir and output a list of card names
    drafted = []
    for filename in glob.glob(os.path.join(draft_dir, "*.txt")):
        with open(filename, "r", encoding="utf-8") as f:
            drafted_card = []
            for line in f:
                card = line.strip()
                # Remove "1 " prefix and handle special cases
                if card.startswith("1 "):
                    card = card[2:]
                if card == "Fire":
                    card = "Fire // Ice"
                # Remove empty lines
                if card.strip():
                    drafted_card.append(card)
            drafted.extend(drafted_card)

    print(f"DRAFTED ({len(drafted)}) = {drafted}")

    # Extract owned cards from owned.dek (XML), only Cards.name fields
    owned = parse_dek_file(get_owned_path()).keys()

    def normalize_name(card_name):
        return card_name.lower().replace("&", "and").strip()

    normalized_owned = set(normalize_name(n) for n in owned)
    rentals = [card for card in drafted if normalize_name(card) not in normalized_owned]

    print(f"RENTALS ({len(rentals)}) = {rentals}")
    if len(rentals) > 100:
        print("Error: More than 100 rentals required.")
        sys.exit(1)

    # 4. Write rentals.txt
    with open(rentals_path, "w", encoding="utf-8") as outfile:
        for line in rentals:
            outfile.write(line + "\n")

def parse_dek_file(filename):
    """
    Reads a .dek file and returns a mapping of card name to CatId.
    """
    tree = ET.parse(filename)
    root = tree.getroot()
    card_map = {}
    for card in root.findall('Cards'):
        name = card.attrib.get('Name')
        catid = card.attrib.get('CatID')
        if name in card_map:
            print(f"Warning: Duplicate card name '{name}' found in {filename} (existing CatID: {card_map[name]}, new CatID: {catid})")
        if name and catid:
            card_map[name] = catid
        else: print(f"Warning: Missing Name or CatID in card element: {ET.tostring(card, encoding='unicode')}")
    return card_map

if __name__ == "__main__":
    main()

