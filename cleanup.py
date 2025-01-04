import os
import shutil

# Walk through all directories and subdirectories
for root, dirs, files in os.walk(".", topdown=False):
    for dir_name in dirs:
        if dir_name == "__pycache__":
            pycache_path = os.path.join(root, dir_name)
            print(f"Removing: {pycache_path}")
            # Remove all files and subdirectories in the __pycache__ directory
            shutil.rmtree(pycache_path)
