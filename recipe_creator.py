#!/usr/bin/env python3
"""Recipe Creator for kalorme.github.io — generates recipe HTML pages.

Run directly with Python, or compile to EXE:
    pip install pyinstaller
    pyinstaller --onefile --windowed recipe_creator.py
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json, re, shutil, sys, webbrowser
import html as html_mod
from pathlib import Path

# ─── Site directory detection ─────────────────────────────────────────────────
if getattr(sys, 'frozen', False):
    _BASE = Path(sys.executable).parent
else:
    _BASE = Path(__file__).parent

# ─── Category options ─────────────────────────────────────────────────────────
TYPE_OPTS    = ['Meal', 'Side', 'Soup', 'Bread', 'Dessert', 'Drink', 'Sauce', 'Other']
PROTEIN_OPTS = ['Pork', 'Beef', 'Chicken', 'Mince', 'Sausage', 'Seafood', 'Veggy']
CUISINE_OPTS = sorted([
    'Albanian','American','Argentinian','Austrian','Belgian','Chinese',
    'English','French','Georgian','German','Greek','Indian','Indonesian',
    'Italian','Japanese','Korean','Laotian','Malaysian','Mexican',
    'Mongolian','Polish','Russian','Spanish','Surinamese','Taiwanese',
    'Thai','Turkish','Vietnamese',
])

TEMPLATE_CSS   = '\n        *, *::before, *::after { box-sizing: border-box; text-size-adjust: none; }\n\n        :root {\n            --bg: #ffffff;\n            --surface: #f5f5f5;\n            --nav-bg: #ffffff;\n            --nav-text: #444444;\n            --accent: #E05A2B;\n            --text: #111111;\n            --text-2: #555555;\n            --text-3: rgba(0,0,0,0.35);\n            --text-4: rgba(0,0,0,0.18);\n            --border: rgba(0,0,0,0.1);\n            --shadow: none;\n            --radius: 10px;\n        }\n\n        @media (prefers-color-scheme: dark) {\n            :root {\n                --bg: #111111;\n                --surface: #1a1a1a;\n                --nav-bg: #0a0a0a;\n                --nav-text: rgba(255,255,255,0.6);\n                --text: rgba(255,255,255,0.92);\n                --text-2: rgba(255,255,255,0.5);\n                --text-3: rgba(255,255,255,0.28);\n                --text-4: rgba(255,255,255,0.14);\n                --border: rgba(255,255,255,0.09);\n                --shadow: none;\n            }\n        }\n\n        html, body {\n            margin: 0;\n            padding: 0;\n            background: var(--bg);\n            color: var(--text);\n            font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', sans-serif;\n            line-height: 1.6;\n            font-size: 17px;\n        }\n\n        a { color: var(--accent); text-decoration: none; font-weight: 600; }\n        h1, h3 { margin: 0; padding: 0; }\n        strong { color: var(--text); font-weight: 700; }\n        sup, sub { position: relative; font-size: 0.6em; line-height: 1; }\n        sup { top: 0.1em; } sub { bottom: 0.3em; }\n        ol, ul { list-style: none; margin: 0; padding: 0; }\n\n        /* NAV BAR */\n        nav {\n            background: var(--nav-bg);\n            height: 50px;\n            display: flex;\n            align-items: center;\n            padding: 0 24px;\n            position: sticky;\n            top: 0;\n            z-index: 100;\n            border-bottom: 1px solid var(--border);\n        }\n        nav a {\n            color: var(--nav-text);\n            font-size: 0.85rem;\n            font-weight: 600;\n            display: flex;\n            align-items: center;\n            gap: 7px;\n            transition: color 0.15s;\n        }\n        nav a:hover { color: var(--text); }\n        nav .accent { color: var(--accent); }\n\n        /* RECIPE IMAGE — banner on mobile, side panel on desktop */\n        #title > span:first-child {\n            display: block !important;\n            width: 100%;\n            height: 260px;\n            padding-top: 0 !important;\n            background-size: contain;\n            background-position: center;\n            background-repeat: no-repeat;\n            background-color: var(--surface);\n        }\n\n        /* MAIN */\n        main { display: block; padding-bottom: 60px; }\n\n        /* TITLE SECTION */\n        #title { border-bottom: 1px solid var(--border); overflow: hidden; }\n        #title .title {\n            padding: 28px 32px 28px;\n            max-width: 1160px;\n            margin: 0 auto;\n        }\n        #title h1 {\n            font-size: clamp(1.8rem, 3.5vw, 2.8rem);\n            font-weight: 800;\n            line-height: 1.1;\n            letter-spacing: -0.8px;\n            margin-bottom: 20px;\n        }\n\n        /* Desktop: image as side panel, fixed aspect-ratio so full image always shows */\n        @media (min-width: 780px) {\n            #title {\n                display: flex;\n                flex-direction: row-reverse;\n                align-items: flex-start;\n            }\n            #title > span:first-child {\n                flex: 0 0 40%;\n                aspect-ratio: 4 / 3;\n                height: auto;\n                width: auto;\n                background-size: contain;\n            }\n            #title .title {\n                flex: 1;\n                max-width: none;\n                margin: 0;\n                padding: 32px 40px;\n            }\n        }\n\n        /* INFO BAR */\n        #info {\n            display: flex;\n            flex-wrap: wrap;\n            align-items: center;\n            margin: 0 0 18px;\n            padding: 0;\n            overflow: visible;\n            font-size: 0.82rem;\n            font-weight: 600;\n            margin-left: 0;\n            gap: 4px 0;\n        }\n        #info .group {\n            display: inline-flex;\n            align-items: center;\n            position: static;\n            white-space: nowrap;\n            line-height: 1;\n            padding: 4px 0;\n        }\n        #info .group + .group::before {\n            content: \'\';\n            display: inline-block;\n            width: 1px;\n            height: 16px;\n            background: var(--border);\n            margin: 0 14px;\n            vertical-align: middle;\n        }\n        #info .info {\n            display: inline-flex;\n            align-items: center;\n            height: auto;\n            line-height: 1;\n            padding: 5px 0;\n            color: var(--text-2);\n            text-decoration: none;\n            position: relative;\n        }\n        #info .info.labeled {\n            flex-direction: column;\n            align-items: flex-start;\n            gap: 3px;\n            padding: 4px 0;\n        }\n        #info .info.labeled + .info.labeled { margin-left: 20px; }\n        #info .info.labeled span { color: var(--text); font-size: 0.9rem; line-height: 1; display: block; }\n        #info .info.labeled label { font-size: 0.6rem; text-transform: uppercase; letter-spacing: 0.9px; color: var(--text-3); display: block; font-weight: 700; }\n        #info .info.icon { padding-left: 26px; }\n        #info .info.icon:after {\n            opacity: 0.5;\n            content: \' \';\n            position: absolute;\n            left: 0;\n            top: 50%;\n            transform: translateY(-50%);\n            width: 18px;\n            height: 18px;\n            background-size: 16px 16px;\n            background-position: center;\n            background-repeat: no-repeat;\n        }\n        @media (prefers-color-scheme: dark) {\n            #info .info.icon:after { filter: invert(100%); opacity: 0.65; }\n        }\n\n        /* DESCRIPTION */\n        .description { font-size: 0.95rem; color: var(--text-2); line-height: 1.75; }\n        .description p { margin: 0; }\n\n        /* RECIPE BODY */\n        #recipe-body {\n            display: grid;\n            grid-template-columns: 1fr;\n            padding: 0 18px;\n            gap: 0;\n            align-items: start;\n        }\n\n        /* INGREDIENTS */\n        #ingredients {\n            padding-top: 28px;\n            margin-bottom: 28px;\n        }\n        #ingredients::before {\n            content: \'Ingredients\';\n            display: block;\n            font-size: 0.8rem;\n            font-weight: 700;\n            text-transform: uppercase;\n            letter-spacing: 0.8px;\n            color: var(--accent);\n            margin-bottom: 12px;\n        }\n        #ingredients > span:first-child { display: none !important; }\n        #ingredients > div {\n            background: transparent;\n            border-radius: 0;\n            padding: 0;\n            box-shadow: none;\n            max-width: none;\n            margin: 0;\n            position: static;\n        }\n        #ingredients > div::before { display: none !important; }\n        .ingredients ul { list-style: none; margin: 0; padding: 0; }\n        .ingredients li {\n            font-size: 0.95rem;\n            color: var(--text-2);\n            line-height: 1.45;\n            margin: 0;\n            padding: 12px 0;\n            border-bottom: 1px solid var(--border);\n        }\n        .ingredients li:last-child { border-bottom: none; }\n        .ingredients li strong { color: var(--text); font-weight: 700; }\n        .ingredients li i {\n            display: block;\n            font-size: 0.8rem;\n            color: var(--text-2);\n            font-style: italic;\n            margin-top: 3px;\n            opacity: 0.65;\n        }\n        .ingredients h3 {\n            font-size: 0.78rem;\n            font-weight: 700;\n            text-transform: uppercase;\n            letter-spacing: 0.8px;\n            color: var(--text-3);\n            padding: 18px 0 4px;\n            margin: 0;\n        }\n\n        /* MULTIPLIER */\n        .multiplier {\n            display: flex;\n            align-items: center;\n            justify-content: space-between;\n            padding-bottom: 14px;\n            margin-bottom: 14px;\n            border-bottom: 1px solid var(--border);\n        }\n        .mult-label {\n            font-size: 0.62rem;\n            font-weight: 700;\n            text-transform: uppercase;\n            letter-spacing: 1px;\n            color: var(--text-3);\n        }\n        .mult-buttons { display: flex; gap: 4px; }\n        .mult-btn {\n            background: var(--border);\n            border: none;\n            color: var(--text-2);\n            border-radius: 6px;\n            padding: 3px 8px;\n            font-size: 0.7rem;\n            font-weight: 700;\n            cursor: pointer;\n            transition: background 0.15s, color 0.15s;\n        }\n        .mult-btn:hover { background: rgba(255,107,53,0.15); color: var(--accent); }\n        .mult-btn.active { background: var(--accent); color: white; }\n\n        /* INSTRUCTIONS */\n        #instructions { padding-top: 28px; }\n        #instructions::before {\n            content: \'Instructions\';\n            display: block;\n            font-size: 0.8rem;\n            font-weight: 700;\n            text-transform: uppercase;\n            letter-spacing: 0.8px;\n            color: var(--accent);\n            margin-bottom: 16px;\n        }\n        #instructions > div {\n            max-width: none;\n            margin: 0;\n            padding: 0;\n            position: static;\n        }\n        #instructions > div::before { display: none !important; }\n        .instructions ol { list-style: none; counter-reset: step; margin: 0; padding: 0; }\n        .instructions ol li {\n            counter-increment: step;\n            display: grid;\n            grid-template-columns: 32px 1fr;\n            column-gap: 16px;\n            align-items: start;\n            padding: 18px 0;\n            font-size: 1rem;\n            color: var(--text-2);\n            line-height: 1.72;\n            border-bottom: 1px solid var(--border);\n        }\n        .step-img {\n            grid-column: 2;\n            width: 100%;\n            height: 220px;\n            object-fit: cover;\n            border-radius: 10px;\n            margin-top: 8px;\n            display: block;\n        }\n        .instructions ol li:last-child { border-bottom: none; }\n        .instructions ol li::before {\n            content: counter(step, decimal-leading-zero);\n            display: block;\n            font-size: 0.7rem;\n            font-weight: 700;\n            letter-spacing: 0.5px;\n            color: var(--accent);\n            margin-top: 5px;\n            line-height: 1;\n        }\n        .instructions h3 {\n            font-size: 0.82rem;\n            font-weight: 700;\n            text-transform: uppercase;\n            letter-spacing: 0.8px;\n            color: var(--text-3);\n            padding: 28px 0 4px;\n            margin: 0;\n            border-top: none;\n            margin-top: 0;\n        }\n        .instructions > div > h3:first-child { border-top: none; margin-top: 0; padding-top: 0; }\n        .instructions > div > *:first-child { padding-top: 0; }\n        .instructions .notes { font-style: italic; color: var(--text-3); }\n\n\n        /* DESKTOP — sticky sidebar, title + instructions scroll freely */\n        @media (min-width: 780px) {\n            #recipe-body {\n                grid-template-columns: 300px 1fr;\n                align-items: start;\n                gap: 0;\n                padding: 0;\n                max-width: none;\n                margin: 0;\n            }\n            #ingredients {\n                position: sticky;\n                top: 50px;\n                height: calc(100vh - 50px);\n                overflow-y: auto;\n                border-right: 1px solid var(--border);\n                padding: 28px 24px 60px;\n                margin-bottom: 0;\n                scrollbar-width: thin;\n                scrollbar-color: var(--border) transparent;\n            }\n            #ingredients::before { margin-bottom: 14px; }\n            #instructions {\n                padding: 28px 48px 100px;\n            }\n            #instructions::before { margin-bottom: 20px; }\n        }\n\n        /* MOBILE */\n        @media (max-width: 779px) {\n            #ingredients { padding-top: 0; }\n            #ingredients::before { padding-top: 28px; }\n            #instructions { padding-top: 0; }\n            #instructions::before { padding-top: 24px; }\n        }\n        @media (max-width: 600px) {\n            #title .title { padding: 20px 18px 20px; }\n        }\n\n        /* THEME TOGGLE BUTTON */\n        #theme-toggle {\n            margin-left: auto;\n            background: none;\n            border: none;\n            cursor: pointer;\n            font-size: 1.1rem;\n            padding: 5px 7px;\n            border-radius: 7px;\n            line-height: 1;\n            transition: background 0.15s;\n        }\n        #theme-toggle:hover { background: var(--border); }\n\n        /* DATA-THEME OVERRIDES (manual toggle beats system preference) */\n        html[data-theme="light"] {\n            --bg: #ffffff; --surface: #f5f5f5; --nav-bg: #ffffff;\n            --nav-text: #444444; --text: #111111; --text-2: #555555;\n            --text-3: rgba(0,0,0,0.35); --text-4: rgba(0,0,0,0.18);\n            --border: rgba(0,0,0,0.1); --shadow: none;\n        }\n        html[data-theme="dark"] {\n            --bg: #111111; --surface: #1a1a1a; --nav-bg: #0a0a0a;\n            --nav-text: rgba(255,255,255,0.6); --text: rgba(255,255,255,0.92);\n            --text-2: rgba(255,255,255,0.5); --text-3: rgba(255,255,255,0.28);\n            --text-4: rgba(255,255,255,0.14); --border: rgba(255,255,255,0.09);\n            --shadow: none;\n        }\n\n        /* Icon filter overrides for when manual theme contradicts system preference.\n           Base icons are black PNGs. Dark mode needs invert() to make them white.\n           These rules ensure the filter matches the actual background, not just the OS setting. */\n        html[data-theme="light"] #info .info.icon:after {\n            filter: none !important;\n            opacity: 0.55;\n        }\n        html[data-theme="dark"] #info .info.icon:after {\n            filter: invert(100%) !important;\n            opacity: 0.65;\n        }\n    '
ICON_SOURCE    = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADwAAAA8CAYAAAA6/NlyAAAEs2lUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4KPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iWE1QIENvcmUgNS41LjAiPgogPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4KICA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIgogICAgeG1sbnM6ZXhpZj0iaHR0cDovL25zLmFkb2JlLmNvbS9leGlmLzEuMC8iCiAgICB4bWxuczp0aWZmPSJodHRwOi8vbnMuYWRvYmUuY29tL3RpZmYvMS4wLyIKICAgIHhtbG5zOnBob3Rvc2hvcD0iaHR0cDovL25zLmFkb2JlLmNvbS9waG90b3Nob3AvMS4wLyIKICAgIHhtbG5zOnhtcD0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wLyIKICAgIHhtbG5zOnhtcE1NPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvbW0vIgogICAgeG1sbnM6c3RFdnQ9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZUV2ZW50IyIKICAgZXhpZjpQaXhlbFhEaW1lbnNpb249IjYwIgogICBleGlmOlBpeGVsWURpbWVuc2lvbj0iNjAiCiAgIGV4aWY6Q29sb3JTcGFjZT0iMSIKICAgdGlmZjpJbWFnZVdpZHRoPSI2MCIKICAgdGlmZjpJbWFnZUxlbmd0aD0iNjAiCiAgIHRpZmY6UmVzb2x1dGlvblVuaXQ9IjIiCiAgIHRpZmY6WFJlc29sdXRpb249IjcyLzEiCiAgIHRpZmY6WVJlc29sdXRpb249IjcyLzEiCiAgIHBob3Rvc2hvcDpDb2xvck1vZGU9IjMiCiAgIHBob3Rvc2hvcDpJQ0NQcm9maWxlPSJzUkdCIElFQzYxOTY2LTIuMSIKICAgeG1wOk1vZGlmeURhdGU9IjIwMjItMDQtMjlUMTQ6MzE6NDIrMDI6MDAiCiAgIHhtcDpNZXRhZGF0YURhdGU9IjIwMjItMDQtMjlUMTQ6MzE6NDIrMDI6MDAiPgogICA8eG1wTU06SGlzdG9yeT4KICAgIDxyZGY6U2VxPgogICAgIDxyZGY6bGkKICAgICAgc3RFdnQ6YWN0aW9uPSJwcm9kdWNlZCIKICAgICAgc3RFdnQ6c29mdHdhcmVBZ2VudD0iQWZmaW5pdHkgRGVzaWduZXIgMS4xMC40IgogICAgICBzdEV2dDp3aGVuPSIyMDIyLTA0LTI5VDE0OjMxOjQyKzAyOjAwIi8+CiAgICA8L3JkZjpTZXE+CiAgIDwveG1wTU06SGlzdG9yeT4KICA8L3JkZjpEZXNjcmlwdGlvbj4KIDwvcmRmOlJERj4KPC94OnhtcG1ldGE+Cjw/eHBhY2tldCBlbmQ9InIiPz750iYKAAABgWlDQ1BzUkdCIElFQzYxOTY2LTIuMQAAKJF1kd8rg1EYxz/2I2IacSG5WBpXm4YSKWXSqKU1U4ab7bUfapu395203Cq3ihI3fl3wF3CrXCtFpORSrokb1ut5bTXJntNzns/5nvM8nfMcsEQySla3+SCby2vhgN81G51z1T5jox07zQzHFF0dDYWCVLWPO2rMeOM1a1U/9681LCZ0BWrqhEcUVcsLTwgHV/OqydvCrUo6tih8KuzR5ILCt6YeL/GLyakSf5msRcJjYGkSdqV+cfwXK2ktKywvx53NrCjl+5gvcSRyM9MSO8U70AkTwI+LScYZY4BehmQewEsfPbKiSr7vJ3+KZclVZFYpoLFEijR5PKKuSPWExKToCRkZCmb///ZVT/b3lao7/GB/Moy3LqjdguKmYXweGkbxCKyPcJGr5C8fwOC76JsVzb0PznU4u6xo8R0434C2BzWmxX4kq7glmYTXE2iMQss11M+Xelbe5/geImvyVVewuwfdct658A1r12foZo16awAAAAlwSFlzAAALEwAACxMBAJqcGAAAAgBJREFUaIHt2jtrVEEYh/Gfxkvwhk1EC8HCzkJBxaCFIOIHEMVCUGxMZSFaCDYi6Eew0o9gI1h5w8pb4QcIaBMQNBYaJRgxWmyCm+NudN8ZIjm8DyzLnOX9n3l2dmYPzJAkSZIkyf9iRYWMzRjFTmzEUIXMbn5gCuN4jk8lYSXCQ7iAcxgu6cQATOM2bmE2ElAyGjdxBqsKMgZlNQ5gBE8iASuDNz6I4z2ufw3mDcop7IsURoVP9Lh2FXtxL5g5KCcjRVHh3T2uvcRPvApmDsqeSFFUeCRYV5NQH6LCa4N1NQn9M0SFly0p3HZSuO2kcNtJ4baTwm0nhdtOCredFG47Kdx2UriA9XPvGypmLsa3SFHNbZIbeICzFTMX412kqKbwrrnXUhHa4Viuc/gF7kQKa+/8fcFHnS2XGsxih4UD8xpj+B4JrCU8hSt4pJ4sbMfDrvYMLursE4eoJXzdwo7V4nCj/VRwsZqn1hx+XCmnydZG+21pYFS4+bOtfa5jnplGe0tpYFT4c6N9rLQjfRhvtI8qlI6OzBFs62qP6qzOE4JPQH2YwGm/t2fXYD+e+fNL/yeip3jO41Kfz2qu0vTu4zQuCyyUUeFNuK/CnCpgEocGLSqZw2N4H6yvQWiwSlbXD7ir83Q1jHU6c63G6b6/MYlreLME90qSJEmSJInxC7BoQlQyr544AAAAAElFTkSuQmCC'
ICON_SERVINGS  = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADwAAAA8CAYAAAA6/NlyAAAEs2lUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4KPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iWE1QIENvcmUgNS41LjAiPgogPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4KICA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIgogICAgeG1sbnM6ZXhpZj0iaHR0cDovL25zLmFkb2JlLmNvbS9leGlmLzEuMC8iCiAgICB4bWxuczp0aWZmPSJodHRwOi8vbnMuYWRvYmUuY29tL3RpZmYvMS4wLyIKICAgIHhtbG5zOnBob3Rvc2hvcD0iaHR0cDovL25zLmFkb2JlLmNvbS9waG90b3Nob3AvMS4wLyIKICAgIHhtbG5zOnhtcD0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wLyIKICAgIHhtbG5zOnhtcE1NPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvbW0vIgogICAgeG1sbnM6c3RFdnQ9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZUV2ZW50IyIKICAgZXhpZjpQaXhlbFhEaW1lbnNpb249IjYwIgogICBleGlmOlBpeGVsWURpbWVuc2lvbj0iNjAiCiAgIGV4aWY6Q29sb3JTcGFjZT0iMSIKICAgdGlmZjpJbWFnZVdpZHRoPSI2MCIKICAgdGlmZjpJbWFnZUxlbmd0aD0iNjAiCiAgIHRpZmY6UmVzb2x1dGlvblVuaXQ9IjIiCiAgIHRpZmY6WFJlc29sdXRpb249IjcyLzEiCiAgIHRpZmY6WVJlc29sdXRpb249IjcyLzEiCiAgIHBob3Rvc2hvcDpDb2xvck1vZGU9IjMiCiAgIHBob3Rvc2hvcDpJQ0NQcm9maWxlPSJzUkdCIElFQzYxOTY2LTIuMSIKICAgeG1wOk1vZGlmeURhdGU9IjIwMjItMDQt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'
ICON_TIMER     = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADwAAAA8CAYAAAA6/NlyAAAEs2lUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4KPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iWE1QIENvcmUgNS41LjAiPgogPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4KICA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIgogICAgeG1sbnM6ZXhpZj0iaHR0cDovL25zLmFkb2JlLmNvbS9leGlmLzEuMC8iCiAgICB4bWxuczp0aWZmPSJodHRwOi8vbnMuYWRvYmUuY29tL3RpZmYvMS4wLyIKICAgIHhtbG5zOnBob3Rvc2hvcD0iaHR0cDovL25zLmFkb2JlLmNvbS9waG90b3Nob3AvMS4wLyIKICAgIHhtbG5zOnhtcD0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wLyIKICAgIHhtbG5zOnhtcE1NPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvbW0vIgogICAgeG1sbnM6c3RFdnQ9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZUV2ZW50IyIKICAgZXhpZjpQaXhlbFhEaW1lbnNpb249IjYwIgogICBleGlmOlBpeGVsWURpbWVuc2lvbj0iNjAiCiAgIGV4aWY6Q29sb3JTcGFjZT0iMSIKICAgdGlmZjpJbWFnZVdpZHRoPSI2MCIKICAgdGlmZjpJbWFnZUxlbmd0aD0iNjAiCiAgIHRpZmY6UmVzb2x1dGlvblVuaXQ9IjIiCiAgIHRpZmY6WFJlc29sdXRpb249IjcyLzEiCiAgIHRpZmY6WVJlc29sdXRpb249IjcyLzEiCiAgIHBob3Rvc2hvcDpDb2xvck1vZGU9IjMiCiAgIHBob3Rvc2hvcDpJQ0NQcm9maWxlPSJzUkdCIElFQzYxOTY2LTIuMSIKICAgeG1wOk1vZGlmeURhdGU9IjIwMjItMDQt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'


# ─── HTML generation ─────────────────────────────────────────────────────────
def make_filename(title: str) -> str:
    safe = re.sub(r'[<>:"/\\|?*]', '', title).strip()
    return safe.replace(' ', '_') + '.html'

def esc(text) -> str:
    return html_mod.escape(str(text), quote=True)

def build_ingredients_html(rows: list) -> str:
    out, ul_open = [], False
    for row in rows:
        if row['type'] == 'header':
            if ul_open:
                out.append('</ul>'); ul_open = False
            out.append(f'<h3 itemprop="recipeIngredient">{esc(row["text"])}</h3>')
        else:
            if not ul_open:
                out.append('<ul>'); ul_open = True
            qty  = row.get('qty',  '').strip()
            unit = row.get('unit', '').strip()
            name = row.get('name', '').strip()
            note = row.get('note', '').strip()
            li = '<li itemprop="recipeIngredient">'
            if qty:
                li += f'<strong>{esc(qty)}</strong>'
                if unit:
                    li += f' <strong>{esc(unit)}</strong>'
                li += ' '
            li += esc(name)
            if note:
                li += f' <i>{esc(note)}</i>'
            li += '</li>'
            out.append(li)
    if ul_open:
        out.append('</ul>')
    return ''.join(out)

def build_instructions_html(rows: list) -> str:
    out, ol_open = [], False
    for row in rows:
        if row['type'] == 'header':
            if ol_open:
                out.append('</ol>'); ol_open = False
            out.append(f'<h3>{esc(row["text"])}</h3>')
        else:
            if not ol_open:
                out.append('<ol>'); ol_open = True
            out.append(f'<li>{esc(row["text"])}</li>')
    if ol_open:
        out.append('</ol>')
    return ''.join(out)

def build_jsonld(data: dict) -> dict:
    jld = {'@type': 'Recipe'}
    if data.get('title'):       jld['name']            = data['title']
    if data.get('description'): jld['description']     = data['description']
    if data.get('servings'):    jld['recipeYield']      = data['servings']
    if data.get('prep'):        jld['prepTime']         = data['prep']
    if data.get('cook'):        jld['cookTime']         = data['cook']
    if data.get('total'):       jld['totalTime']        = data['total']
    if data.get('source_url'):  jld['mainEntityOfPage'] = data['source_url']
    ingr = []
    for r in data.get('ingredients', []):
        if r['type'] == 'ingredient' and r.get('name'):
            parts = [p for p in [r.get('qty',''), r.get('unit',''), r.get('name',''),
                                  f"({r['note']})" if r.get('note') else ''] if p]
            ingr.append(' '.join(parts))
    if ingr: jld['recipeIngredient'] = ingr
    steps = [r['text'] for r in data.get('instructions', []) if r['type'] == 'step' and r.get('text')]
    if steps: jld['recipeInstructions'] = steps
    return jld

def build_html(data: dict) -> str:
    title         = data['title']
    filename_base = make_filename(title).replace('.html', '')
    img_path      = f'./images/{filename_base}.jpg'

    # Info bar
    groups = []
    if data.get('source_url'):
        domain = re.sub(r'^https?://(www\.)?', '', data['source_url']).split('/')[0]
        groups.append(
            f'<span class="group"><a class="info icon source" href="{esc(data["source_url"])}">'
            f'{esc(domain)}</a></span>'
        )
    if data.get('servings'):
        groups.append(f'<span class="group"><span class="info icon servings">{esc(data["servings"])}</span></span>')
    time_parts = []
    if data.get('prep'):  time_parts.append(('Prep',  data['prep'],  'icon timer'))
    if data.get('cook'):  time_parts.append(('Cook',  data['cook'],  ''))
    if data.get('total'): time_parts.append(('Total', data['total'], ''))
    if time_parts:
        spans = ''.join(
            f'<span class="info labeled{" " + cls if cls else ""}">'
            f'<span>{esc(t)}</span><label>{esc(lbl)}</label></span>'
            for lbl, t, cls in time_parts
        )
        groups.append(f'<span class="group">{spans}</span>')

    desc      = data.get('description', '').strip()
    desc_html = f'<div class="description"><p>{esc(desc)}</p></div>' if desc else ''
    info_html = ''.join(groups)

    ingr_html  = build_ingredients_html(data.get('ingredients', []))
    instr_html = build_instructions_html(data.get('instructions', []))
    jsonld     = json.dumps(build_jsonld(data), ensure_ascii=False, indent=2)

    icon_css = (
        f".icon.source:after {{ background-image: url('{ICON_SOURCE}'); }}\n"
        f"        .icon.servings:after {{ background-image: url('{ICON_SERVINGS}'); }}\n"
        f"        .icon.timer:after {{ background-image: url('{ICON_TIMER}'); }}"
    )

    return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no">
    <title>{esc(title)}</title>
    <style>
{TEMPLATE_CSS}
    </style>

    <script type="application/ld+json">
    {jsonld}
    </script>
</head>
<body>

    <nav>
        <a href="index.html">
            <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                <path d="M19 12H5M12 5l-7 7 7 7"/>
            </svg>
            <span>\U0001f373 <span class="accent">Moutstraat</span></span>
        </a>
        <button id="theme-toggle" title="Toggle theme"></button>
    </nav>

    <main>

        <div id="title"><span></span><div class="title"><h1>{esc(title)}</h1><p id="info">{info_html}</p>{desc_html}</div></div>

        <div id="recipe-body">
            <div id="ingredients"><span></span><div class="ingredients">{ingr_html}</div></div>
            <div id="instructions"><div class="instructions">{instr_html}</div></div>
        </div>

    </main>

    <style type="text/css">
        {icon_css}
        main > div > span:first-child {{ background-image: url("{img_path}"); }}
    </style>
    <script>
    (function () {{
        const root = document.documentElement;
        const stored = localStorage.getItem(\'theme\');
        if (stored) root.setAttribute(\'data-theme\', stored);
        function isDark() {{
            const t = root.getAttribute(\'data-theme\');
            return t === \'dark\' || (!t && window.matchMedia(\'(prefers-color-scheme: dark)\').matches);
        }}
        function updateBtn(btn) {{
            btn.textContent = isDark() ? \'☀️\' : \'\U0001f319\';
            btn.title = isDark() ? \'Switch to light mode\' : \'Switch to dark mode\';
        }}
        document.addEventListener(\'DOMContentLoaded\', () => {{
            const btn = document.getElementById(\'theme-toggle\');
            if (!btn) return;
            updateBtn(btn);
            btn.addEventListener(\'click\', () => {{
                const next = isDark() ? \'light\' : \'dark\';
                root.setAttribute(\'data-theme\', next);
                localStorage.setItem(\'theme\', next);
                updateBtn(btn);
            }});
        }});
    }})();

    const STEP_IMAGES = {{}};
    document.addEventListener(\'DOMContentLoaded\', () => {{
        const steps = document.querySelectorAll(\'.instructions ol li\');
        steps.forEach((li, i) => {{
            const src = STEP_IMAGES[i + 1];
            if (!src) return;
            const img = document.createElement(\'img\');
            img.src = src; img.alt = \'Step \' + (i + 1); img.className = \'step-img\';
            li.appendChild(img);
        }});
        const ingredientItems = document.querySelectorAll(\'.ingredients li\');
        const origQtys = Array.from(ingredientItems).map(li => {{
            const s = li.querySelector(\'strong\');
            if (!s) return null;
            const n = parseFloat(s.textContent.trim());
            return isNaN(n) ? null : {{ el: s, val: n }};
        }});
        const multiplierEl = document.createElement(\'div\');
        multiplierEl.className = \'multiplier\';
        multiplierEl.innerHTML =
            \'<span class="mult-label">Servings</span>\' +
            \'<div class="mult-buttons">\' +
            \'<button class="mult-btn active" data-mult="1">1\xd7</button>\' +
            \'<button class="mult-btn" data-mult="2">2\xd7</button>\' +
            \'<button class="mult-btn" data-mult="3">3\xd7</button>\' +
            \'</div>\';
        const ingrCard = document.querySelector(\'#ingredients > div\');
        if (ingrCard) ingrCard.insertBefore(multiplierEl, ingrCard.firstChild);
        multiplierEl.addEventListener(\'click\', e => {{
            const btn = e.target.closest(\'.mult-btn\');
            if (!btn) return;
            multiplierEl.querySelectorAll(\'.mult-btn\').forEach(b => b.classList.remove(\'active\'));
            btn.classList.add(\'active\');
            const mult = parseFloat(btn.dataset.mult);
            origQtys.forEach(q => {{
                if (!q) return;
                const v = q.val * mult;
                q.el.textContent = Number.isInteger(v) ? v : +v.toFixed(2);
            }});
        }});
    }});
    </script>

</body>
</html>'''


def update_metadata(data: dict, site_dir: Path):
    meta_path = site_dir / 'recipe_metadata.json'
    try:
        metadata = json.loads(meta_path.read_text(encoding='utf-8'))
    except Exception:
        metadata = {}
    filename  = make_filename(data['title'])
    ingr_names = sorted({r.get('name', '') for r in data.get('ingredients', [])
                          if r['type'] == 'ingredient' and r.get('name')})
    metadata[filename] = {
        'title':       data['title'],
        'category':    data.get('categories', []),
        'ingredients': ingr_names,
    }
    meta_path.write_text(json.dumps(dict(sorted(metadata.items())), indent=4, ensure_ascii=False),
                          encoding='utf-8')


# ─── GUI constants ────────────────────────────────────────────────────────────
PAD      = 8
BG_ROOT  = '#F0EDE8'
BG_CARD  = '#FFFFFF'
ACCENT   = '#E05A2B'
ACCENT_D = '#C04A1E'
FG       = '#1C1C1E'
FG_MUTED = '#6E6E73'
BORDER   = '#D1CFC9'
FONT     = ('Segoe UI', 10)
FONT_SM  = ('Segoe UI', 9)
FONT_BOLD = ('Segoe UI', 10, 'bold')
FONT_H1   = ('Segoe UI', 15, 'bold')
FONT_H2   = ('Segoe UI', 12, 'bold')


def section_label(parent, text: str) -> tk.Frame:
    f = tk.Frame(parent, bg=BG_ROOT)
    tk.Label(f, text=text, font=FONT_H2, bg=BG_ROOT, fg=FG).pack(side='left')
    sep = tk.Frame(f, bg=BORDER, height=1)
    sep.pack(side='left', fill='x', expand=True, padx=(10, 0), pady=(6, 0))
    return f


class ScrollFrame(tk.Frame):
    def __init__(self, parent, bg=BG_ROOT, **kw):
        super().__init__(parent, bg=bg, **kw)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
        sb = ttk.Scrollbar(self, orient='vertical', command=self.canvas.yview)
        self.inner = tk.Frame(self.canvas, bg=bg)
        self._win  = self.canvas.create_window((0, 0), window=self.inner, anchor='nw')
        self.canvas.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')
        self.canvas.pack(side='left', fill='both', expand=True)
        self.inner.bind('<Configure>', self._update_scroll)
        self.canvas.bind('<Configure>', self._resize_inner)
        self.canvas.bind('<Enter>', lambda _: self.canvas.bind_all('<MouseWheel>', self._wheel))
        self.canvas.bind('<Leave>', lambda _: self.canvas.unbind_all('<MouseWheel>'))

    def _update_scroll(self, _): self.canvas.configure(scrollregion=self.canvas.bbox('all'))
    def _resize_inner(self, e):  self.canvas.itemconfig(self._win, width=e.width)
    def _wheel(self, e):         self.canvas.yview_scroll(int(-1*(e.delta/120)), 'units')


class IngredientEditor(tk.Frame):
    def __init__(self, parent, **kw):
        super().__init__(parent, bg=BG_ROOT, **kw)
        self.rows = []
        bar = tk.Frame(self, bg=BG_ROOT)
        self._btn(bar, '+ Ingredient',     self.add_ingredient, bg=ACCENT, fg='white').pack(side='left', padx=(0,4))
        self._btn(bar, '+ Section Header', self.add_header,     bg='#E8E4DE', fg=FG).pack(side='left')
        bar.pack(fill='x', pady=(0, 6))
        sf = ScrollFrame(self, bg=BG_ROOT)
        sf.pack(fill='both', expand=True)
        self.container = sf.inner

    @staticmethod
    def _btn(parent, text, cmd, bg=ACCENT, fg='white'):
        return tk.Button(parent, text=text, command=cmd, font=FONT_SM, cursor='hand2',
                         bg=bg, fg=fg, activebackground=ACCENT_D, activeforeground='white',
                         relief='flat', padx=10, pady=5, bd=0)

    def add_ingredient(self): self._add('ingredient')
    def add_header(self):     self._add('header')

    def _add(self, row_type, *, qty='', unit='', name='', note='', text=''):
        row = {'type': row_type}
        f   = tk.Frame(self.container, bg=BG_CARD, highlightthickness=1, highlightbackground=BORDER)
        row['frame'] = f

        badge_fg = ACCENT if row_type == 'header' else FG_MUTED
        tk.Label(f, text='HDR' if row_type == 'header' else 'INGR',
                 font=('Segoe UI', 7, 'bold'), bg=BG_CARD, fg=badge_fg, width=4
                 ).grid(row=0, column=0, padx=(6, 4), pady=6)
        col = 1
        if row_type == 'ingredient':
            for v_init, w, _ in [(qty,5,'Qty'),(unit,7,'Unit')]:
                v = tk.StringVar(value=v_init)
                key = ('qty' if w==5 else 'unit')
                row[key] = v
                tk.Entry(f, textvariable=v, width=w, font=FONT, relief='flat',
                         bg='#F5F3EF', fg=FG, insertbackground=FG,
                         highlightthickness=1, highlightbackground=BORDER
                         ).grid(row=0, column=col, padx=2, pady=6, ipady=3)
                col += 1
            for v_init, w, key in [(name,26,'name'),(note,20,'note')]:
                v = tk.StringVar(value=v_init)
                row[key] = v
                tk.Entry(f, textvariable=v, width=w, font=FONT if key=='name' else FONT_SM,
                         relief='flat', bg='#F5F3EF',
                         fg=FG if key=='name' else FG_MUTED, insertbackground=FG,
                         highlightthickness=1, highlightbackground=BORDER
                         ).grid(row=0, column=col, padx=2, pady=6, ipady=3)
                col += 1
        else:
            v = tk.StringVar(value=text); row['text'] = v
            tk.Entry(f, textvariable=v, width=58, font=FONT_BOLD, relief='flat',
                     bg='#FFF8F5', fg=ACCENT, insertbackground=ACCENT,
                     highlightthickness=1, highlightbackground=BORDER
                     ).grid(row=0, column=col, padx=2, pady=6, ipady=3, columnspan=4)
            col += 4

        mv = tk.Frame(f, bg=BG_CARD)
        tk.Button(mv, text='▲', font=('Segoe UI',8), command=lambda: self._move(row,-1),
                  relief='flat', bg=BG_CARD, fg=FG_MUTED, cursor='hand2', padx=2).pack(side='top')
        tk.Button(mv, text='▼', font=('Segoe UI',8), command=lambda: self._move(row,+1),
                  relief='flat', bg=BG_CARD, fg=FG_MUTED, cursor='hand2', padx=2).pack(side='top')
        mv.grid(row=0, column=col, padx=2); col += 1
        tk.Button(f, text='✕', font=FONT_SM, command=lambda: self._delete(row),
                  relief='flat', bg=BG_CARD, fg='#CC3333', cursor='hand2'
                  ).grid(row=0, column=col, padx=(2,8))

        self.rows.append(row)
        self._repack()

    def _delete(self, row):
        row['frame'].destroy(); self.rows.remove(row)

    def _move(self, row, d):
        i = self.rows.index(row); n = i + d
        if 0 <= n < len(self.rows):
            self.rows[i], self.rows[n] = self.rows[n], self.rows[i]
            self._repack()

    def _repack(self):
        for r in self.rows: r['frame'].pack_forget()
        for r in self.rows: r['frame'].pack(fill='x', pady=2, padx=2)

    def get_data(self) -> list:
        out = []
        for r in self.rows:
            if r['type'] == 'header':
                out.append({'type':'header', 'text': r['text'].get()})
            else:
                out.append({'type':'ingredient', 'qty': r['qty'].get(),
                             'unit': r['unit'].get(), 'name': r['name'].get(),
                             'note': r['note'].get()})
        return out


class InstructionEditor(tk.Frame):
    def __init__(self, parent, **kw):
        super().__init__(parent, bg=BG_ROOT, **kw)
        self.rows = []
        bar = tk.Frame(self, bg=BG_ROOT)
        tk.Button(bar, text='+ Step', command=self.add_step, font=FONT_SM, cursor='hand2',
                  bg=ACCENT, fg='white', activebackground=ACCENT_D, activeforeground='white',
                  relief='flat', padx=10, pady=5, bd=0).pack(side='left', padx=(0,4))
        tk.Button(bar, text='+ Section Header', command=self.add_header, font=FONT_SM,
                  cursor='hand2', bg='#E8E4DE', fg=FG, relief='flat',
                  padx=10, pady=5, bd=0).pack(side='left')
        bar.pack(fill='x', pady=(0,6))
        sf = ScrollFrame(self, bg=BG_ROOT)
        sf.pack(fill='both', expand=True)
        self.container = sf.inner

    def add_step(self):   self._add('step')
    def add_header(self): self._add('header')

    def _add(self, row_type, *, text=''):
        row = {'type': row_type}
        f   = tk.Frame(self.container, bg=BG_CARD, highlightthickness=1, highlightbackground=BORDER)
        row['frame'] = f
        n = sum(1 for r in self.rows if r['type']=='step') + 1
        badge_text = 'HDR' if row_type=='header' else str(n)
        badge_fg   = ACCENT if row_type=='header' else FG_MUTED
        lbl = tk.Label(f, text=badge_text, font=('Segoe UI',8,'bold'),
                       bg=BG_CARD, fg=badge_fg, width=4)
        lbl.grid(row=0, column=0, padx=(6,4), pady=6)
        row['badge'] = lbl
        v = tk.StringVar(value=text); row['text'] = v
        txt_bg = '#FFF8F5' if row_type=='header' else '#F5F3EF'
        txt_fg = ACCENT    if row_type=='header' else FG
        entry = tk.Entry(f, textvariable=v, font=FONT_BOLD if row_type=='header' else FONT,
                         relief='flat', bg=txt_bg, fg=txt_fg, insertbackground=txt_fg,
                         highlightthickness=1, highlightbackground=BORDER)
        entry.grid(row=0, column=1, padx=2, pady=6, ipady=3, sticky='ew')
        f.columnconfigure(1, weight=1)
        mv = tk.Frame(f, bg=BG_CARD)
        tk.Button(mv, text='▲', font=('Segoe UI',8), command=lambda: self._move(row,-1),
                  relief='flat', bg=BG_CARD, fg=FG_MUTED, cursor='hand2', padx=2).pack(side='top')
        tk.Button(mv, text='▼', font=('Segoe UI',8), command=lambda: self._move(row,+1),
                  relief='flat', bg=BG_CARD, fg=FG_MUTED, cursor='hand2', padx=2).pack(side='top')
        mv.grid(row=0, column=2, padx=2)
        tk.Button(f, text='✕', font=FONT_SM, command=lambda: self._delete(row),
                  relief='flat', bg=BG_CARD, fg='#CC3333', cursor='hand2'
                  ).grid(row=0, column=3, padx=(2,8))
        self.rows.append(row)
        self._repack()

    def _delete(self, row):
        row['frame'].destroy(); self.rows.remove(row); self._renumber()

    def _move(self, row, d):
        i = self.rows.index(row); n = i + d
        if 0 <= n < len(self.rows):
            self.rows[i], self.rows[n] = self.rows[n], self.rows[i]
            self._repack(); self._renumber()

    def _repack(self):
        for r in self.rows: r['frame'].pack_forget()
        for r in self.rows: r['frame'].pack(fill='x', pady=2, padx=2)

    def _renumber(self):
        n = 1
        for r in self.rows:
            if r['type']=='step':
                r['badge'].config(text=str(n)); n += 1

    def get_data(self) -> list:
        return [{'type': r['type'], 'text': r['text'].get()} for r in self.rows]


# ─── Main application ─────────────────────────────────────────────────────────
class RecipeCreatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Recipe Creator — Moutstraat')
        self.geometry('1040x780')
        self.minsize(820, 620)
        self.configure(bg=BG_ROOT)
        self._last_output = None

        self._site_dir   = tk.StringVar(value=str(_BASE))
        self._image_path = tk.StringVar()
        self._title_v    = tk.StringVar()
        self._source_v   = tk.StringVar()
        self._servings_v = tk.StringVar()
        self._prep_v     = tk.StringVar()
        self._cook_v     = tk.StringVar()
        self._total_v    = tk.StringVar()
        self._status_var = tk.StringVar(value='Ready.')

        self._type_vars    = {o: tk.BooleanVar() for o in TYPE_OPTS}
        self._protein_vars = {o: tk.BooleanVar() for o in PROTEIN_OPTS}
        self._cuisine_vars = {o: tk.BooleanVar() for o in CUISINE_OPTS}

        self._build_ui()

    def _build_ui(self):
        # Top bar
        top = tk.Frame(self, bg='#1A1A1A')
        top.pack(fill='x')
        tk.Label(top, text='\U0001f373 Recipe Creator', font=FONT_H1, bg='#1A1A1A', fg='white').pack(side='left', padx=16, pady=12)
        tk.Label(top, text='Moutstraat', font=('Segoe UI',11), bg='#1A1A1A', fg=ACCENT).pack(side='left', pady=12)

        # Style notebook
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TNotebook', background=BG_ROOT, borderwidth=0)
        style.configure('TNotebook.Tab', font=FONT_BOLD, padding=[14,7], background='#E0DDD8', foreground=FG_MUTED)
        style.map('TNotebook.Tab', background=[('selected', BG_CARD)], foreground=[('selected', FG)])

        nb = ttk.Notebook(self)
        nb.pack(fill='both', expand=True)

        tab_info  = ScrollFrame(nb, bg=BG_ROOT)
        tab_ingr  = tk.Frame(nb, bg=BG_ROOT)
        tab_instr = tk.Frame(nb, bg=BG_ROOT)
        nb.add(tab_info,  text='  Basic Info  ')
        nb.add(tab_ingr,  text='  Ingredients  ')
        nb.add(tab_instr, text='  Instructions  ')

        self._build_info_tab(tab_info.inner)
        self._build_ingr_tab(tab_ingr)
        self._build_instr_tab(tab_instr)

        # Bottom bar
        bot = tk.Frame(self, bg='#ECEAE5', pady=10)
        bot.pack(fill='x', side='bottom')
        tk.Label(bot, textvariable=self._status_var, font=FONT_SM, bg='#ECEAE5', fg=FG_MUTED).pack(side='left', padx=16)
        tk.Button(bot, text='Generate Recipe', command=self._generate, font=FONT_BOLD,
                  bg=ACCENT, fg='white', activebackground=ACCENT_D, activeforeground='white',
                  relief='flat', padx=20, pady=8, cursor='hand2').pack(side='right', padx=16)
        tk.Button(bot, text='Open in Browser', command=self._open_preview, font=FONT_SM,
                  bg='#D1CFC9', fg=FG, relief='flat', padx=12, pady=8, cursor='hand2').pack(side='right', padx=(0,6))

    def _build_info_tab(self, parent):
        p = tk.Frame(parent, bg=BG_ROOT, padx=24, pady=16)
        p.pack(fill='both', expand=True)
        p.columnconfigure(1, weight=1)
        p.columnconfigure(3, weight=1)

        row = 0
        section_label(p, 'Recipe Details').grid(row=row, column=0, columnspan=4, sticky='ew', pady=(0,12)); row+=1

        # Title
        tk.Label(p, text='Title *', font=FONT_SM, bg=BG_ROOT, fg=FG_MUTED, anchor='w').grid(row=row, column=0, sticky='w', padx=(0,8), pady=4)
        tk.Entry(p, textvariable=self._title_v, font=('Segoe UI',11,'bold'), width=40, relief='flat',
                 bg='#FFF', fg=FG, insertbackground=FG, highlightthickness=1,
                 highlightbackground=BORDER, highlightcolor=ACCENT).grid(row=row, column=1, columnspan=3, sticky='ew', pady=4, ipady=5)
        row+=1

        # Site dir
        tk.Label(p, text='Site Directory', font=FONT_SM, bg=BG_ROOT, fg=FG_MUTED, anchor='w').grid(row=row, column=0, sticky='w', padx=(0,8), pady=4)
        df = tk.Frame(p, bg=BG_ROOT)
        tk.Entry(df, textvariable=self._site_dir, font=FONT_SM, width=40, relief='flat',
                 bg='#FFF', fg=FG, highlightthickness=1, highlightbackground=BORDER).pack(side='left', fill='x', expand=True, ipady=4)
        tk.Button(df, text='Browse…', command=self._browse_dir, font=FONT_SM, relief='flat',
                  bg='#E8E4DE', fg=FG, padx=8, pady=4, cursor='hand2').pack(side='left', padx=(4,0))
        df.grid(row=row, column=1, columnspan=3, sticky='ew', pady=4); row+=1

        # Image
        tk.Label(p, text='Recipe Image', font=FONT_SM, bg=BG_ROOT, fg=FG_MUTED, anchor='w').grid(row=row, column=0, sticky='w', padx=(0,8), pady=4)
        imgf = tk.Frame(p, bg=BG_ROOT)
        tk.Entry(imgf, textvariable=self._image_path, font=FONT_SM, width=40, relief='flat',
                 bg='#FFF', fg=FG, highlightthickness=1, highlightbackground=BORDER).pack(side='left', fill='x', expand=True, ipady=4)
        tk.Button(imgf, text='Browse…', command=self._browse_image, font=FONT_SM, relief='flat',
                  bg='#E8E4DE', fg=FG, padx=8, pady=4, cursor='hand2').pack(side='left', padx=(4,0))
        imgf.grid(row=row, column=1, columnspan=3, sticky='ew', pady=4); row+=1

        # Source
        tk.Label(p, text='Source URL', font=FONT_SM, bg=BG_ROOT, fg=FG_MUTED, anchor='w').grid(row=row, column=0, sticky='w', padx=(0,8), pady=4)
        tk.Entry(p, textvariable=self._source_v, font=FONT, width=40, relief='flat',
                 bg='#FFF', fg=FG, insertbackground=FG, highlightthickness=1, highlightbackground=BORDER
                 ).grid(row=row, column=1, columnspan=3, sticky='ew', pady=4, ipady=4); row+=1

        # Servings + Times on same row
        tk.Label(p, text='Servings', font=FONT_SM, bg=BG_ROOT, fg=FG_MUTED, anchor='w').grid(row=row, column=0, sticky='w', padx=(0,8), pady=4)
        tk.Entry(p, textvariable=self._servings_v, font=FONT, width=16, relief='flat',
                 bg='#FFF', fg=FG, insertbackground=FG, highlightthickness=1, highlightbackground=BORDER
                 ).grid(row=row, column=1, sticky='w', pady=4, ipady=4)
        tk.Label(p, text='Times', font=FONT_SM, bg=BG_ROOT, fg=FG_MUTED, anchor='w').grid(row=row, column=2, sticky='w', padx=(16,8), pady=4)
        tf = tk.Frame(p, bg=BG_ROOT)
        for lbl, var in [('Prep', self._prep_v), ('Cook', self._cook_v), ('Total', self._total_v)]:
            tk.Label(tf, text=lbl, font=FONT_SM, bg=BG_ROOT, fg=FG_MUTED).pack(side='left', padx=(0,3))
            tk.Entry(tf, textvariable=var, width=8, font=FONT, relief='flat',
                     bg='#FFF', fg=FG, highlightthickness=1, highlightbackground=BORDER
                     ).pack(side='left', padx=(0,12), ipady=4)
        tf.grid(row=row, column=3, sticky='w', pady=4); row+=1

        # Description
        tk.Label(p, text='Description', font=FONT_SM, bg=BG_ROOT, fg=FG_MUTED, anchor='nw').grid(row=row, column=0, sticky='nw', padx=(0,8), pady=(8,4))
        self._desc_text = tk.Text(p, width=55, height=4, font=FONT, relief='flat',
                                   bg='#FFF', fg=FG, insertbackground=FG,
                                   highlightthickness=1, highlightbackground=BORDER,
                                   wrap='word', pady=6, padx=6)
        self._desc_text.grid(row=row, column=1, columnspan=3, sticky='ew', pady=(8,4)); row+=1

        # Categories
        section_label(p, 'Categories').grid(row=row, column=0, columnspan=4, sticky='ew', pady=(16,10)); row+=1

        for label, var_dict in [('Type', self._type_vars), ('Protein', self._protein_vars)]:
            tk.Label(p, text=label, font=FONT_SM, bg=BG_ROOT, fg=FG_MUTED, anchor='w', width=10).grid(row=row, column=0, sticky='w', pady=3)
            cf = tk.Frame(p, bg=BG_ROOT)
            for name, var in var_dict.items():
                tk.Checkbutton(cf, text=name, variable=var, font=FONT_SM, bg=BG_ROOT, fg=FG,
                               activebackground=BG_ROOT, selectcolor='white', cursor='hand2'
                               ).pack(side='left', padx=(0,5))
            cf.grid(row=row, column=1, columnspan=3, sticky='w', pady=3); row+=1

        tk.Label(p, text='Cuisine', font=FONT_SM, bg=BG_ROOT, fg=FG_MUTED, anchor='nw', width=10).grid(row=row, column=0, sticky='nw', pady=3)
        cuis_outer = tk.Frame(p, bg=BG_ROOT)
        line1 = tk.Frame(cuis_outer, bg=BG_ROOT)
        line2 = tk.Frame(cuis_outer, bg=BG_ROOT)
        items = list(self._cuisine_vars.items())
        half  = (len(items)+1)//2
        for name, var in items[:half]:
            tk.Checkbutton(line1, text=name, variable=var, font=FONT_SM, bg=BG_ROOT, fg=FG,
                           activebackground=BG_ROOT, selectcolor='white', cursor='hand2'
                           ).pack(side='left', padx=(0,4))
        for name, var in items[half:]:
            tk.Checkbutton(line2, text=name, variable=var, font=FONT_SM, bg=BG_ROOT, fg=FG,
                           activebackground=BG_ROOT, selectcolor='white', cursor='hand2'
                           ).pack(side='left', padx=(0,4))
        line1.pack(fill='x'); line2.pack(fill='x')
        cuis_outer.grid(row=row, column=1, columnspan=3, sticky='w', pady=3)

    def _build_ingr_tab(self, parent):
        p = tk.Frame(parent, bg=BG_ROOT, padx=16, pady=12)
        p.pack(fill='both', expand=True)
        tk.Label(p, text='INGR  Qty   Unit   Ingredient Name               Note (optional)',
                 font=FONT_SM, bg=BG_ROOT, fg=FG_MUTED).pack(anchor='w', pady=(0,6))
        self.ingr_editor = IngredientEditor(p)
        self.ingr_editor.pack(fill='both', expand=True)

    def _build_instr_tab(self, parent):
        p = tk.Frame(parent, bg=BG_ROOT, padx=16, pady=12)
        p.pack(fill='both', expand=True)
        tk.Label(p, text='Enter each cooking step. Add Section Headers to group steps (e.g. "For the Sauce").',
                 font=FONT_SM, bg=BG_ROOT, fg=FG_MUTED).pack(anchor='w', pady=(0,6))
        self.instr_editor = InstructionEditor(p)
        self.instr_editor.pack(fill='both', expand=True)

    def _browse_dir(self):
        d = filedialog.askdirectory(title='Select site directory', initialdir=self._site_dir.get())
        if d: self._site_dir.set(d)

    def _browse_image(self):
        f = filedialog.askopenfilename(
            title='Select recipe image',
            filetypes=[('Images', '*.jpg *.jpeg *.png *.webp'), ('All files', '*.*')]
        )
        if f: self._image_path.set(f)

    def _collect(self) -> dict:
        cats = (
            [k for k,v in self._type_vars.items()    if v.get()] +
            [k for k,v in self._protein_vars.items() if v.get()] +
            [k for k,v in self._cuisine_vars.items() if v.get()]
        )
        return {
            'title':        self._title_v.get().strip(),
            'source_url':   self._source_v.get().strip(),
            'servings':     self._servings_v.get().strip(),
            'prep':         self._prep_v.get().strip(),
            'cook':         self._cook_v.get().strip(),
            'total':        self._total_v.get().strip(),
            'description':  self._desc_text.get('1.0', 'end').strip(),
            'categories':   cats,
            'ingredients':  self.ingr_editor.get_data(),
            'instructions': self.instr_editor.get_data(),
        }

    def _generate(self):
        data = self._collect()
        if not data['title']:
            messagebox.showerror('Missing field', 'Please enter a recipe title.'); return
        site_dir = Path(self._site_dir.get())
        if not site_dir.is_dir():
            messagebox.showerror('Bad directory', f'Site directory not found:\n{site_dir}'); return

        filename    = make_filename(data['title'])
        output_path = site_dir / filename

        # Copy image
        img_src = self._image_path.get().strip()
        if img_src:
            src_path = Path(img_src)
            if src_path.exists():
                dest = site_dir / 'images' / (filename.replace('.html', '.jpg'))
                dest.parent.mkdir(exist_ok=True)
                shutil.copy2(src_path, dest)
            else:
                messagebox.showwarning('Image not found', f'Image not found:\n{img_src}\n\nContinuing without image.')

        output_path.write_text(build_html(data), encoding='utf-8')

        try:
            update_metadata(data, site_dir)
        except Exception as e:
            messagebox.showwarning('Metadata warning', f'Could not update recipe_metadata.json:\n{e}')

        self._last_output = output_path
        self._status_var.set(f'✓ Saved: {filename}')
        messagebox.showinfo('Done!', f'Recipe created!\n\n{output_path}\n\nClick "Open in Browser" to preview.')

    def _open_preview(self):
        if self._last_output and self._last_output.exists():
            webbrowser.open(self._last_output.as_uri())
        else:
            messagebox.showinfo('No preview', 'Generate a recipe first.')


if __name__ == '__main__':
    app = RecipeCreatorApp()
    app.mainloop()
