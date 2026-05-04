#!/usr/bin/env python3
"""
update_recipe_layout.py

Converts all recipe HTML files to use the new layout from Agedashi_Tofu.html,
preserving each recipe's content (title, ingredients, instructions, image).

Usage:
    python3 update_recipe_layout.py
"""
import re
from pathlib import Path

BASE = Path(__file__).parent
TEMPLATE_FILE = BASE / 'Agedashi_Tofu.html'

# Skip the template source and any non-recipe pages
SKIP = {'Agedashi_Tofu.html', 'index.html'}


# ── Helpers ────────────────────────────────────────────────────────────────────

def read(path: Path) -> str:
    return path.read_text(encoding='utf-8')

def write(path: Path, content: str):
    path.write_text(content, encoding='utf-8')

def get_title(html: str) -> str:
    m = re.search(r'<title>(.*?)</title>', html)
    return m.group(1) if m else 'Recipe'

def find_div(html: str, id_: str):
    """
    Find <div ... id="id_" ...>...</div> and return (start, end) byte offsets.
    Correctly handles nested divs.
    """
    m = re.search(rf'<div\b[^>]*\bid="{re.escape(id_)}"[^>]*>', html)
    if not m:
        return None, None

    depth = 0
    base = m.start()
    for tag in re.finditer(r'<div\b|</div>', html[base:]):
        if tag.group().startswith('</'):
            depth -= 1
            if depth == 0:
                return base, base + tag.end()
        else:
            depth += 1
    return None, None

def extract_div(html: str, id_: str) -> str:
    s, e = find_div(html, id_)
    return html[s:e] if s is not None else ''

def replace_div(html: str, id_: str, replacement: str) -> str:
    """Swap out <div id="id_">...</div> in html with replacement text."""
    s, e = find_div(html, id_)
    if s is None:
        print(f'    ⚠  could not find #{id_}')
        return html
    return html[:s] + replacement + html[e:]

def set_external_image_css(html: str, stem: str) -> str:
    """Replace the hero image CSS rule with an external file reference."""
    new_rule = f'main > div > span:first-child {{ background-image: url("./images/{stem}.jpg"); }}'
    return re.sub(
        r'main\s*>\s*div\s*>\s*span:first-child\s*\{[^}]*\}',
        new_rule, html, flags=re.DOTALL
    )


# ── Conversion ─────────────────────────────────────────────────────────────────

def convert(src_path: Path, template: str) -> str:
    src = read(src_path)

    title      = get_title(src)
    title_div  = extract_div(src, 'title')
    ingr_div   = extract_div(src, 'ingredients')
    instr_div  = extract_div(src, 'instructions')

    if not title_div:
        raise ValueError('missing #title div')
    if not ingr_div:
        raise ValueError('missing #ingredients div')
    if not instr_div:
        raise ValueError('missing #instructions div')

    # Drop nutrition table if present
    instr_div = re.sub(
        r'<div class="nutrition">.*?</div>', '', instr_div, flags=re.DOTALL
    )

    result = template

    # 1. Page <title>
    result = re.sub(r'<title>[^<]*</title>', f'<title>{title}</title>', result)

    # 2. Swap content divs (each re-searches the already-updated string)
    result = replace_div(result, 'title',        title_div)
    result = replace_div(result, 'ingredients',  ingr_div)
    result = replace_div(result, 'instructions', instr_div)

    # 3. Set external image reference (./images/<stem>.jpg)
    result = set_external_image_css(result, src_path.stem)

    # 4. Clear the Agedashi Tofu JSON-LD (wrong metadata for other recipes)
    result = re.sub(
        r'(<script type="application/ld\+json">).*?(</script>)',
        r'\1{}\2',
        result, flags=re.DOTALL
    )

    return result


# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    if not TEMPLATE_FILE.exists():
        print(f'ERROR: template not found at {TEMPLATE_FILE}')
        return

    template = read(TEMPLATE_FILE)
    files = sorted(f for f in BASE.glob('*.html') if f.name not in SKIP)

    print(f'Template: {TEMPLATE_FILE.name}')
    print(f'Converting {len(files)} recipe files...\n')

    ok = errors = 0
    for path in files:
        print(f'  {path.name} ... ', end='', flush=True)
        try:
            new_html = convert(path, template)
            write(path, new_html)
            print('ok')
            ok += 1
        except Exception as exc:
            print(f'FAILED — {exc}')
            errors += 1

    print(f'\nDone: {ok} converted, {errors} failed.')


if __name__ == '__main__':
    main()
