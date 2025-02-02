import os
import difflib

def rename_files(folder_x, folder_y):
    # List all the .jpg files in folder_x
    jpg_files = [f for f in os.listdir(folder_x) if f.endswith('.jpg')]
    
    # List all the .html files in folder_y
    html_files = [f for f in os.listdir(folder_y) if f.endswith('.html')]
    
    # Strip the file extensions from the html files
    html_base_names = [os.path.splitext(f)[0] for f in html_files]

    # Iterate over the .jpg files and try to find a match with the .html files
    for jpg in jpg_files:
        jpg_base_name = os.path.splitext(jpg)[0]  # Get the base name of the jpg file
        
        # Use difflib to find the closest match for jpg_base_name in html_base_names
        closest_match = difflib.get_close_matches(jpg_base_name, html_base_names, n=1, cutoff=0.6)  # Adjust cutoff for similarity

        if closest_match:
            # Get the best match
            matched_html_base_name = closest_match[0]
            new_name = f"{matched_html_base_name}.jpg"
            
            old_path = os.path.join(folder_x, jpg)
            new_path = os.path.join(folder_x, new_name)
            
            # Rename the file
            os.rename(old_path, new_path)
            print(f"Renamed {old_path} to {new_path}")
        else:
            print(f"No close match found for {jpg_base_name}")

# Usage example:
# Usage example:
folder_x = r'C:\Users\Koen\Documents\GitHub\kalorme.github.io\images\recipe'  # Replace with the path to your folder containing .jpg files
folder_y = r'C:\Users\Koen\Documents\GitHub\kalorme.github.io'  # Replace with the path to your folder containing .html files

rename_files(folder_x, folder_y)