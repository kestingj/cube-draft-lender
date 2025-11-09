import os
import sys

from file_helpers import BASE_DIR

def create_directory(name):
    name = name.strip()
    if not name:
        print("No name provided.")
        return
    dir_path = os.path.join(BASE_DIR, name)
    try:
        os.makedirs(dir_path, exist_ok=False)
        print(f"Directory created at: {dir_path}")
    except FileExistsError:
        print("Directory already exists.")
    except Exception as e:
        print(f"Error creating directory: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python setup-draft.py <directory_name>")
    else:
        create_directory(sys.argv[1])