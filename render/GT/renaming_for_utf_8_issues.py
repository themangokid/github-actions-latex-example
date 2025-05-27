import os

def replace_chars(text):
    return text.replace('o', 'o').replace('a', 'a').replace('_a', '_a')

def process_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        new_content = replace_chars(content)
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated content: {filepath}")
    except (UnicodeDecodeError, PermissionError, FileNotFoundError):
        print(f"Skipped (binary/inaccessible): {filepath}")

def rename_path(path):
    dirpath, name = os.path.split(path)
    new_name = replace_chars(name)
    new_path = os.path.join(dirpath, new_name)
    if new_path != path:
        try:
            os.rename(path, new_path)
            print(f"Renamed: {path} -> {new_path}")
        except (PermissionError, FileNotFoundError, OSError) as e:
            print(f"Failed to rename {path}: {e}")
    return new_path

def process_directory(root_dir):
    # Walk bottom-up so directories are renamed last
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        # Rename and process files
        for filename in filenames:
            original_path = os.path.join(dirpath, filename)
            renamed_file_path = rename_path(original_path)
            process_file(renamed_file_path)

        # Rename directories after their contents
        for dirname in dirnames:
            original_dir_path = os.path.join(dirpath, dirname)
            rename_path(original_dir_path)

if __name__ == "__main__":
    root = os.path.abspath("./")
    process_directory(root)
