import os
from PIL import Image
import customtkinter as ctk

# Cache for loaded images so we don't reload them multiple times
_icon_cache = {}

def get_icon(name, size=(24, 24)):
    """
    Load an icon from the assets/icons folder and return a CTkImage.
    """
    key = f"{name}_{size[0]}x{size[1]}"
    if key in _icon_cache:
        return _icon_cache[key]
    
    # Calculate path relative to this file
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    icon_path = os.path.join(base_dir, "assets", "icons", f"{name}.png")
    
    if not os.path.exists(icon_path):
        print(f"Warning: Icon {name}.png not found at {icon_path}")
        return None
        
    try:
        pil_image = Image.open(icon_path)
        ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=size)
        _icon_cache[key] = ctk_image
        return ctk_image
    except Exception as e:
        print(f"Error loading icon {name}: {e}")
        return None
