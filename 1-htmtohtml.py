import os

def rename_htm_to_html(folder_path):
    # Iterate through all files in the folder
    for filename in os.listdir(folder_path):
        # Check if the file has a .htm extension
        if filename.endswith(".htm"):
            # Create the new filename by replacing .htm with .html
            new_filename = filename[:-4] + ".html"
            
            # Get the full paths for the old and new filenames
            old_file_path = os.path.join(folder_path, filename)
            new_file_path = os.path.join(folder_path, new_filename)
            
            # Rename the file
            os.rename(old_file_path, new_file_path)
            print(f"Renamed: {filename} -> {new_filename}")

# Specify the folder path where your .htm files are located
folder_path = r"C:\Users\Koen\Documents\GitHub\kalorme.github.io"

# Call the function to rename the files
rename_htm_to_html(folder_path)