import sys
import os
import glob
import time

import xml.etree.ElementTree as ET

from file_helpers import get_draft_dir, get_owned_path, get_downloads_folder
from binder import from_dek_file, from_txt_file, combine_binders

def main():
    if len(sys.argv) != 2:
        print("Usage: python create-trade-binders.py <draft_name>")
        return
    draft_name = sys.argv[1]
    draft_dir = get_draft_dir(draft_name)
    owned_card_binder = from_dek_file(get_owned_path())
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
    rented_binder = from_dek_file(recent_dek_file)
    print(f"RENTED items: {rented_binder.cards}")
    combined_binder = combine_binders(owned_card_binder, rented_binder)
    deck_paths = [f for f in os.listdir(draft_dir) if f.endswith('.txt') and f != 'rentals.txt']
    list_card_mappings = {}

    for deck_txt_path in deck_paths:
        card_names = from_txt_file(os.path.join(draft_dir, deck_txt_path))
        
        trade_binder = combined_binder.get_subset(card_names, deck_txt_path)
        base, _ = os.path.splitext(deck_txt_path)
        trade_binder_path = f"{base}_trade_binder.dek"
        trade_binder.write_to_file(os.path.join(draft_dir, trade_binder_path))
        list_card_mappings[trade_binder_path] = trade_binder.cards

    print(list_card_mappings)

if __name__ == "__main__":
    main()