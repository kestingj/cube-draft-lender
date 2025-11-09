import subprocess
import os

def main():
    draft_name = input("Enter draft name: ")

    # Execute setup-draft.py
    subprocess.run(['python', 'setup-draft.py', draft_name])

    print("Once you have finished drafting, go to Game Logs in Draftmancer and export the draft decks in Format: Card Names to your Downloads folder.")
    input("Press Enter to generate rentals...")

    # Execute find-rentals.py
    subprocess.run(['python', 'find-rentals.py', draft_name])

    print("rentals.txt has been generated in the draft folder. Upload this file to Manatraders to rent missing cards. After you have received the cards, be sure to download your rented .dek file to your Downloads folder.")
    input("Press Enter to generate trade binders...")

    # Execute create-trade-binders.py
    subprocess.run(['python', 'create-trade-binders.py', draft_name])

    print("Trade binders have been created in the draft folder. Import these files as new trade binders on MTGO and open up trades with the other drafters.")

if __name__ == "__main__":
    main()