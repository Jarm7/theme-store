import os
import json
from submit_theme import convert_legacy_preferences

THEMES_FOLDER = "./themes"
THEMES_DATA_FILE = "./themes.json"


def get_color_css_variable(color):
    color_map = {
        "primaryColor": "--zen-colors-primary",
        "secondaryColor": "--zen-colors-secondary",
        "tertiaryColor": "--zen-colors-tertiary",
        "colorsBorder": "--zen-colors-border",
        "dialogBg": "--zen-dialog-background",
        "accentColor": "--zen-primary-color"
    }
    return color_map.get(color, None)


def write_colors(colors_file, output_file):
    with open(colors_file, "r") as f:
        colors = json.load(f)

    with open(output_file, "w") as f:
        f.write("/* This is an auto-generated color theme. */\n")
        f.write(":root {\n")

        for color, value in colors.items():
            if color == "isDarkMode":
                continue
            css_var = get_color_css_variable(color)
            if css_var:
                f.write(f"    {css_var}: {value} !important;\n")

        f.write("}\n")

    return colors


def main():
    themes_data = {}
    with open(THEMES_DATA_FILE, "w") as f:
        json.dump(themes_data, f, indent=4)

    for theme in os.listdir(THEMES_FOLDER):
        theme_folder = os.path.join(THEMES_FOLDER, theme)

        if not os.path.isdir(theme_folder):
            continue

        theme_data_file = os.path.join(theme_folder, "theme.json")
        if not os.path.exists(theme_data_file):
            continue

        with open(theme_data_file, "r") as f:
            theme_data = json.load(f)

        with open(theme_data_file, "w") as f:
            json.dump(theme_data, f, indent=4)

        theme_colors_file = os.path.join(theme_folder, "colors.json")
        if os.path.exists(theme_colors_file):
            print(f"  Found colors.json in theme: {theme}")
            theme_colors_output = os.path.join(theme_folder, "chrome.css")
            colors = write_colors(theme_colors_file, theme_colors_output)

            if "tags" not in theme_data:
                theme_data["tags"] = []
            if "color scheme" not in theme_data["tags"]:
                theme_data["tags"].append("color scheme")

            if "isDarkMode" in colors and colors["isDarkMode"] and "dark" not in theme_data["tags"]:
                theme_data["tags"].append("dark")

        themes_data[theme] = theme_data

        preferences_data_file = os.path.join(theme_folder, "preferences.json")
        if os.path.exists(preferences_data_file):
            print(f"Found preferences.json in theme: {theme}")
            with open(preferences_data_file, "r") as f:
                preferences_data = json.load(f)

            if isinstance(preferences_data, dict):
                print("Legacy preferences found, performing transformation into new structure.")
                preferences_data = convert_legacy_preferences(preferences_data)

            with open(preferences_data_file, "w") as f:
                json.dump(preferences_data, f, indent=4)

        print(f"Rebuilt theme: {theme}")

    with open(THEMES_DATA_FILE, "w") as f:
        json.dump(themes_data, f, indent=4)

    print("Rebuilt all themes!")


if __name__ == "__main__":
    main()
