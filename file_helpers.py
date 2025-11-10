import os

BASE_DIR = os.getcwd()

def get_draft_dir(draft_name: str) -> str:
    return os.path.join(BASE_DIR, "drafts", draft_name)

def get_owned_path() -> str:
    return os.path.join(BASE_DIR, "owned.dek")

def get_downloads_folder() -> str:
    return os.path.expanduser("~/Downloads")

def get_rentals_path(draft_name: str) -> str:
    draft_dir = get_draft_dir(draft_name)
    return os.path.join(draft_dir, "rentals.txt")

def get_rented_dek_path(draft_name: str) -> str:
    draft_dir = get_draft_dir(draft_name)
    return os.path.join(draft_dir, "rented.dek")