import os

BASE_DIR = os.getcwd()

def get_draft_dir(draft_name: str) -> str:
    return os.path.join(BASE_DIR, draft_name)

def get_owned_path() -> str:
    return os.path.join(BASE_DIR, "owned.dek")

def get_downloads_folder() -> str:
    return os.path.expanduser("~/Downloads")