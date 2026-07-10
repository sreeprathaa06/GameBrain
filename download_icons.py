import os
import urllib.request

icons = {
    "home": "https://img.icons8.com/ios-filled/50/ffffff/home.png",
    "game": "https://img.icons8.com/ios-filled/50/ffffff/controller.png",
    "brain": "https://img.icons8.com/ios-filled/50/ffffff/brain.png",
    "dashboard": "https://img.icons8.com/ios-filled/50/ffffff/bar-chart.png",
    "trophy": "https://img.icons8.com/ios-filled/50/ffffff/trophy.png",
    "settings": "https://img.icons8.com/ios-filled/50/ffffff/settings.png",
    "lock": "https://img.icons8.com/ios-filled/50/ffffff/lock.png",
    "robot": "https://img.icons8.com/ios-filled/50/ffffff/bot.png",
    "close": "https://img.icons8.com/ios-filled/50/ffffff/delete-sign.png"
}

icon_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icons")
os.makedirs(icon_dir, exist_ok=True)

for name, url in icons.items():
    file_path = os.path.join(icon_dir, f"{name}.png")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(file_path, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
        print(f"Downloaded {name}.png")
    except Exception as e:
        print(f"Failed to download {name}: {e}")
