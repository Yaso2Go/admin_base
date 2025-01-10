from pathlib import Path

# Get the full path of the current file
current_file_path = Path(__file__)

# Find the base directory (website)
base_dir = current_file_path.parents[3]

print("Base directory:", base_dir)
