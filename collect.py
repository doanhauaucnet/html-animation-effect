import os

# === Configuration ===
whitelist_ext = {'.html'}  # Allowed extensions
blacklist_ext = {}  # Disallowed extensions

output_file = 'collected_code.txt'

def collect_code(root_dir='.'):
    collected = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            file_ext = os.path.splitext(filename)[1].lower()
            
            # Check whitelist and blacklist
            if whitelist_ext and file_ext not in whitelist_ext:
                continue
            if blacklist_ext and file_ext in blacklist_ext:
                continue
            
            file_path = os.path.join(dirpath, filename)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                collected.append((file_path, content))
            except Exception as e:
                print(f"Failed to read {file_path}: {e}")
    
    return collected

def save_to_file(collected, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        for path, content in collected:
            f.write(f"=== {path} ===\n")
            f.write(content)
            f.write("\n\n")

if __name__ == "__main__":
    collected = collect_code()
    save_to_file(collected, output_file)
    print(f"Collected {len(collected)} files into {output_file}")
