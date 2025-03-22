import os
import json
import sys
from typing import Dict

def ensure_version_in_theme(themeFolder: str) -> bool:
    """Process a single theme folder and ensure it has a version."""
    themeDataFile = os.path.join(themeFolder, "theme.json")
    
    if not os.path.exists(themeDataFile):
        print(f"Warning: theme.json not found in {themeFolder}", file=sys.stderr)
        return False
        
    try:
        with open(themeDataFile, "r") as f:
            themeData: Dict = json.load(f)
            
        updated = False
        if "version" not in themeData:
            themeData["version"] = "1.0.0"
            updated = True
            
        if updated:
            with open(themeDataFile, "w") as f:
                json.dump(themeData, f, indent=4)
            return True
        return False
        
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {themeDataFile}: {str(e)}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Unexpected error processing {themeDataFile}: {str(e)}", file=sys.stderr)
        return False

if __name__ == "__main__":
    themes_dir = "themes"
    if not os.path.exists(themes_dir):
        print(f"Error: {themes_dir} directory not found", file=sys.stderr)
        sys.exit(1)

    processed_count = 0
    for themeId in os.listdir("themes"):
        themeFolder = os.path.join("themes", themeId)
        if not os.path.isdir(themeFolder):
            continue
            
        if ensure_version_in_theme(themeFolder):
            print(f"Added version to theme: {themeId}")
            processed_count += 1
            
    print(f"Processing complete. Updated {processed_count} themes.")
