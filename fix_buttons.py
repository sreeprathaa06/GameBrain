import os
import re

def fix_buttons():
    app_dir = os.path.join("c:\\", "Users", "User", "Desktop", "GameBrain2", "app")
    
    # regex to find ctk.CTkButton( and add corner_radius=8, if it doesn't already have one
    # We'll just replace 'ctk.CTkButton(' with 'ctk.CTkButton(corner_radius=8, '
    # But only if it doesn't already have corner_radius inside the same file?
    # A simpler replace:
    
    count = 0
    for root, dirs, files in os.walk(app_dir):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Check if it has ctk.CTkButton
                if "ctk.CTkButton(" in content:
                    # Simple replace, but be careful not to add it multiple times
                    # if the user runs it twice
                    new_content = re.sub(r'ctk\.CTkButton\((?!corner_radius=)', r'ctk.CTkButton(corner_radius=8, ', content)
                    
                    if new_content != content:
                        with open(path, "w", encoding="utf-8") as f:
                            f.write(new_content)
                        count += 1
                        print(f"Updated buttons in: {path}")

    print(f"Total files updated: {count}")

if __name__ == "__main__":
    fix_buttons()
