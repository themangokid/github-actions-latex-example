import os

def replace_chars(text):
    return text.replace('o', 'o').replace('a', 'a').replace('_a', '_a')

def process_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        new_content = replace_chars(content)
        if content != new_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated content: {filepath}")
    except (UnicodeDecodeError, PermissionError):
        pass  # Skip binary or inaccessible files

def rename_path(path):
    dirpath, name = os.path.split(path)
    new_name = replace_chars(name)
    new_path = os.path.join(dirpath, new_name)
    if new_path != path:
        os.rename(path, new_path)
        print(f"Renamed: {path} -> {new_path}")
    return new_path

def process_directory(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        # Process files
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            new_file_path = rename_path(file_path)
            process_file(new_file_path)
        # Process directories
        for dirname in dirnames:
            dir_path = os.path.join(dirpath, dirname)
            rename_path(dir_path)

if __name__ == "__main__":
    current_dir = os.path.abspath('./')
    process_directory(current_dir)
