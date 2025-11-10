import glob
import os
import sys
import xml.etree.ElementTree as ET
from file_helpers import get_draft_dir, get_owned_path, get_rentals_path

from binder import from_dek_file, from_txt_file

def main():

    if len(sys.argv) != 2:
        print("Usage: python find-rentals.py <draft_name>")
        sys.exit(1)

    draft_name = sys.argv[1]
    draft_dir = get_draft_dir(draft_name)
    # rentals_path = "C:/Users/Joseph Kesting/Documents/DiscordDrafts/rentals.txt"
    rentals_path = get_rentals_path(draft_name)

    # Copy .txt files that with the patter: Session_<draft_name>_Deck*.txt from Downloads to draft_dir
    downloads_dir = os.path.expanduser(r"~/Downloads")
    pattern = f"Session_{draft_name}_Deck*.txt"
    dest_dir = draft_dir
    os.makedirs(dest_dir, exist_ok=True)
    for file_path in glob.glob(os.path.join(downloads_dir, pattern)):
        dest_path = os.path.join(dest_dir, os.path.basename(file_path))
        with open(file_path, "rb") as src, open(dest_path, "wb") as dst:
            dst.write(src.read())
    
    # Read all .txt files from draft_dir and output a list of card names
    drafted = []
    for filename in glob.glob(os.path.join(draft_dir, "*.txt")):
        if os.path.basename(filename) != "rentals.txt":
            drafted_deck = from_txt_file(filename)
            drafted.extend(drafted_deck)

    print(f"DRAFTED ({len(drafted)}) = {drafted}")
    
    owned_binder = from_dek_file(get_owned_path())

    owned_card_names = owned_binder.card_names()
    rentals = [card for card in drafted if card not in owned_card_names]

    print(f"RENTALS ({len(rentals)}) = {rentals}")
    if len(rentals) > 100:
        print("Error: More than 100 rentals required.")
        sys.exit(1)

    # 4. Write rentals.txt
    with open(rentals_path, "w", encoding="utf-8") as outfile:
        for line in rentals:
            outfile.write(line + "\n")

if __name__ == "__main__":
    main()

