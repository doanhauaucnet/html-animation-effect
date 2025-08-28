import os
import re
import subprocess

# --- Configuration ---
# The name of the folder containing your animation HTML files.
ANIM_FOLDER = 'Anim'
# The path to your main library HTML file.
LIBRARY_FILE = 'Animation Library.html'
# --- End of Configuration ---

def get_animation_files_from_disk():
    """Scans the animation folder and returns a list of HTML file paths."""
    if not os.path.isdir(ANIM_FOLDER):
        print(f"Error: Directory '{ANIM_FOLDER}' not found.")
        return []
    
    # List all files in the directory, filter for .html files, and prepend the folder path.
    return [os.path.join(ANIM_FOLDER, f) for f in os.listdir(ANIM_FOLDER) if f.endswith('.html')]

def update_library_file(disk_files):
    """
    Reads the library file, checks if the list of animations is up-to-date,
    and updates it if necessary.
    Returns True if the file was changed, False otherwise.
    """
    try:
        with open(LIBRARY_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: Library file '{LIBRARY_FILE}' not found.")
        return False

    # Regex to find the 'animationFiles' array in the script tag.
    # It captures the content between the square brackets.
    regex = r"const animationFiles = \[\s*([^\]]*)\s*\];"
    match = re.search(regex, content)

    if not match:
        print("Error: Could not find the 'animationFiles' array in the library file.")
        return False

    # Extract the file paths currently in the HTML, clean them up.
    # The content is in group 1 of the match.
    html_files_str = match.group(1)
    # Split by comma, strip whitespace and quotes from each entry, and filter out empty strings.
    html_files = [f.strip().strip('"\'') for f in html_files_str.split(',') if f.strip()]
    
    # Convert lists to sets to easily find differences.
    disk_files_set = set(disk_files)
    html_files_set = set(html_files)

    # If the sets are identical, no update is needed.
    if disk_files_set == html_files_set:
        print("Animation library is already up-to-date.")
        return False

    # --- File needs to be updated ---
    print("Updating animation library...")
    
    # Format the new list of files for JavaScript array syntax.
    # Each filename is enclosed in double quotes and separated by a comma and a newline.
    formatted_files = ',\n            '.join([f'"{f}"' for f in sorted(list(disk_files_set))])
    
    # Construct the new array string.
    new_array_str = f"const animationFiles = [\n            {formatted_files}\n        ];"
    
    # Replace the old array string with the new one in the file content.
    updated_content = content.replace(match.group(0), new_array_str)

    try:
        with open(LIBRARY_FILE, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print(f"Successfully updated '{LIBRARY_FILE}'.")
        return True
    except IOError as e:
        print(f"Error writing to file '{LIBRARY_FILE}': {e}")
        return False

def manage_git_repository():
    """
    Checks for git changes, and if any exist, adds, commits, and pushes them.
    The commit message is based on the file changes.
    """
    try:
        # Check the status of the repository.
        # '--porcelain' gives an easy-to-parse output.
        status_result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True, check=True)
        status_output = status_result.stdout.strip()

        if not status_output:
            print("No git changes to commit.")
            return

        print("Git changes detected. Preparing to commit...")

        # --- Determine the commit message ---
        commit_message = "Update animation library" # Default message
        changed_files = status_output.split('\n')
        
        # Prioritize newly added files for the commit message.
        added_files = [line[3:] for line in changed_files if line.startswith('??')]
        if added_files:
            # Use the name of the first new file as the commit message.
            commit_message = f"Add {os.path.basename(added_files[0])}"
        else:
            # If no new files, use the name of the first modified file.
            modified_files = [line[3:] for line in changed_files if line.startswith(' M')]
            if modified_files:
                commit_message = f"Update {os.path.basename(modified_files[0])}"

        # --- Execute Git Commands ---
        print(f"Using commit message: '{commit_message}'")

        # 1. Add all changes
        subprocess.run(['git', 'add', '.'], check=True)
        print("Staged all changes.")

        # 2. Commit the changes
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        print("Committed changes.")

        # 3. Push to the remote repository
        # Using 'gh' to push, as requested. 'git push' would also work.
        subprocess.run(['gh', 'repo', 'sync'], check=True) # `gh repo sync` is a robust way to push/pull
        # Alternatively, a simple push:
        # subprocess.run(['git', 'push'], check=True)
        print("Pushed changes to remote repository.")

    except FileNotFoundError:
        print("Error: 'git' or 'gh' command not found. Make sure Git and GitHub CLI are installed and in your PATH.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running a git command: {e}")
        print(f"Stderr: {e.stderr}")

def main():
    """Main function to run the update process."""
    print("--- Starting Auto-Update Script ---")
    
    # Step 1: Get the list of animation files from the 'Anim' folder.
    disk_files = get_animation_files_from_disk()
    if not disk_files:
        print("No animation files found on disk. Exiting.")
        return

    # Step 2: Update the library HTML file if it's out of sync.
    update_library_file(disk_files)
    
    # Step 3: Check for any git changes (including the one we might have just made) and push.
    manage_git_repository()
    
    print("--- Script Finished ---")


if __name__ == "__main__":
    main()
