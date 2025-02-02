import os
import json
from bs4 import BeautifulSoup

class Recipe:
    def __init__(self, filename, title, ingredients=None, category=None):
        self.filename = filename
        self.title = title
        self.ingredients = ingredients or []
        self.category = category or []

def load_or_create_metadata(metadata_path):
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r') as f:
            return json.load(f)
    return {}

def save_metadata(metadata, metadata_path):
    # Convert to list of items for sorting
    metadata_items = list(metadata.items())
    # Sort by filename (dictionary key)
    metadata_items.sort(key=lambda x: x[0].lower())
    # Convert back to dictionary
    sorted_metadata = dict(metadata_items)
    
    with open(metadata_path, 'w') as f:
        json.dump(sorted_metadata, f, indent=4)

def extract_ingredients_from_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
    
    ingredients_div = soup.find('div', id='ingredients')
    
    if not ingredients_div:
        return []
    
    for h3_tag in ingredients_div.find_all('h3'):
        h3_tag.decompose()
    
    ingredient_list = []
    ingredient_items = ingredients_div.find_all('li', itemprop='recipeIngredient')
    
    for ingredient_item in ingredient_items:
        for strong_tag in ingredient_item.find_all('strong'):
            strong_tag.decompose()
        
        for i_tag in ingredient_item.find_all('i'):
            i_tag.decompose()
        
        cleaned_text = ingredient_item.get_text(separator=" ", strip=True)

        if not cleaned_text:
            continue
        
        cleaned_text = filter_ingredient_text(cleaned_text)
        ingredient_list.append(cleaned_text)

    return sorted(ingredient_list)  # Sort ingredients alphabetically

def filter_ingredient_text(ingredient_text):
    unwanted_prefixes = ["- ", "stalks of ", "of ", "Top with", "Splash of "]
    unwanted_suffixes = [
        " to taste", ", finely diced", ", finely chopped", " chopped", ", softened"
    ]
    
    for prefix in unwanted_prefixes:
        if ingredient_text.startswith(prefix):
            ingredient_text = ingredient_text[len(prefix):]
            break

    for suffix in unwanted_suffixes:
        if ingredient_text.endswith(suffix):
            ingredient_text = ingredient_text[:-len(suffix)]
            break
    
    return ingredient_text.strip()

def update_metadata(folder_path, metadata_path='recipe_metadata.json'):
    metadata = load_or_create_metadata(os.path.join(folder_path, metadata_path))
    
    html_files = [f for f in os.listdir(folder_path) 
                  if f.endswith('.html') and f != 'index.html']
    
    for html_file in html_files:
        file_path = os.path.join(folder_path, html_file)
        ingredients = extract_ingredients_from_html(file_path)
        
        if html_file not in metadata:
            title = ' '.join(word.capitalize() for word in os.path.splitext(html_file)[0].split('_'))
            metadata[html_file] = {
                "title": title,
                "category": ["Uncategorized"],
                "ingredients": ingredients if ingredients else []
            }
        else:
            # Preserve existing title and category, update only ingredients
            metadata[html_file]["ingredients"] = ingredients if ingredients else []
    
    save_metadata(metadata, os.path.join(folder_path, metadata_path))
    print("Metadata updated successfully!")

if __name__ == "__main__":
    folder_path = r"c:\Users\Koen\Documents\GitHub\kalorme.github.io"
    update_metadata(folder_path)