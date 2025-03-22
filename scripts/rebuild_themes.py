import os
import json
import sys
from submit_theme import convert_legacy_preferences
from typing import Dict, Optional

THEMES_FOLDER = "./themes"
THEMES_DATA_FILE = "./themes.json"

COLOR_MAP: Dict[str, str] = {
    "primaryColor": "--zen-colors-primary",
    "secondaryColor": "--zen-colors-secondary",
    "tertiaryColor": "--zen-colors-tertiary",
    "colorsBorder": "--zen-colors-border",
    "dialogBg": "--zen-dialog-background",
    "accentColor": "--zen-primary-color"
}

class UnknownColorError(Exception):
    pass

def get_color_css_variable(color: str) -> str:
    try:
        return COLOR_MAP[color]
    except KeyError:
        print(f"Unknown color: {color}", file=sys.stderr)
        raise UnknownColorError(f"Invalid color key: {color}")

def write_colors(colors_file: str, output_file: str) -> Optional[Dict]:
    try:
        with open(colors_file, "r") as f:
            colors = json.load(f)
        with open(output_file, "w") as f:
            f.write("/* This is an auto generated color theme. */\n")
            f.write(":root {\n")
            for color in colors:
                if color == "isDarkMode":
                    continue
                try:
                    css_var = get_color_css_variable(color)
                    f.write(f"    {css_var}: {colors[color]} !important;\n")
                except UnknownColorError:
                    continue
            f.write("}\n")
        return colors
    except json.JSONDecodeError as e:
        print(f"Error parsing {colors_file}: {str(e)}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error writing colors to {output_file}: {str(e)}", file=sys.stderr)
        return None

def main():
    if not os.path.exists(THEMES_DATA_FILE):
        with open(THEMES_DATA_FILE, "w") as f:
            json.dump({}, f, indent=4)
    processed_count = 0
    if not os.path.exists(THEMES_FOLDER):
        print(f"Error: {THEMES_FOLDER} directory not found", file=sys.stderr)
        sys.exit(1)
    for theme in os.listdir(THEMES_FOLDER):
        theme_folder = os.path.join(THEMES_FOLDER, theme)
        if not os.path.isdir(theme_folder):
            continue
        theme_data_file = os.path.join(theme_folder, "theme.json")
        if not os.path.exists(theme_data_file):
            print(f"Warning: {theme_data_file} not found", file=sys.stderr)
            continue
        try:
            with open(theme_data_file, "r") as f:
                theme_data = json.load(f)
            theme_modified = False
            with open(THEMES_DATA_FILE, "r") as f:
                themes_data = json.load(f)
                theme_colors_file = os.path.join(theme_folder, "colors.json")
                if os.path.exists(theme_colors_file):
                    print(f"  Found colors.json in theme: {theme}")
                    theme_colors_output = os.path.join(theme_folder, "chrome.css")
                    colors = write_colors(theme_colors_file, theme_colors_output)
                    if colors:
                        if "tags" not in theme_data:
                            theme_data["tags"] = []
                            theme_modified = True
                        if "color scheme" not in theme_data["tags"]:
                            theme_data["tags"].append("color scheme")
                            theme_modified = True
                        if "isDarkMode" in colors and colors["isDarkMode"] and "dark" not in theme_data["tags"]:
                            theme_data["tags"].append("dark")
                            theme_modified = True
                themes_data[theme] = theme_data
                with open(THEMES_DATA_FILE, "w") as f:
                    json.dump(themes_data, f, indent=4)
            if theme_modified:
                with open(theme_data_file, "w") as f:
                    json.dump(theme_data, f, indent=4)
            preferences_data_file = os.path.join(theme_folder, "preferences.json")
            if os.path.exists(preferences_data_file):
                print(f"Found preferences.json in theme: {theme}")
                try:
                    with open(preferences_data_file, "r") as f:
                        preferences_data = json.load(f)
                    if isinstance(preferences_data, dict):
                        print("Legacy preferences found, performing transformation into new structure.")
                        preferences_data = convert_legacy_preferences(preferences_data)
                        with open(preferences_data_file, "w") as f:
                            json.dump(preferences_data, f, indent=4)
                except json.JSONDecodeError as e:
                    print(f"Error parsing {preferences_data_file}: {str(e)}", file=sys.stderr)
            print(f"Rebuilt theme: {theme}")
            processed_count += 1
        except json.JSONDecodeError as e:
            print(f"Error parsing {theme_data_file}: {str(e)}", file=sys.stderr)
        except Exception as e:
            print(f"Unexpected error processing theme {theme}: {str(e)}", file=sys.stderr)
    print(f"Rebuilt all themes! Processed {processed_count} themes.")

if __name__ == "__main__":
    main()
