import requests
import os
from git import Repo

# --- SECURE SETTINGS ---
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_USER = "JonielN47"
REPO_NAME = "family-tv"

SOURCE_URL = "https://iptv-org.github.io/iptv/index.m3u"
OUTPUT_FILENAME = "Family_Vibe.m3u"

# Base URL for the world's largest open-source IPTV logo database
LOGO_BASE_URL = "https://iptv-org.github.io/collections/logos/"

# --- SMART CATEGORIES ---
CATEGORIES = {
    "Sports": ["ESPN", "FS1", "GOLF", "NFL", "NBA", "MLB", "STADIUM"],
    "News": ["ABC NEWS", "NBC NEWS", "CBS NEWS", "FOX NEWS", "CNN", "MSNBC", "BLOOMBERG"],
    "Entertainment": ["HBO", "AMC", "TBS", "TNT", "DISNEY", "NICK", "HGTV", "FOOD"]
}

def get_logo_url(channel_name):
    """Guesses the logo URL based on the channel name."""
    # Clean the name: lowercase and replace spaces with dashes
    clean_name = channel_name.lower().replace(" ", "-")
    return f"{LOGO_BASE_URL}{clean_name}.png"

def get_group(channel_name):
    for group, keywords in CATEGORIES.items():
        if any(key.upper() in channel_name.upper() for key in keywords):
            return group
    return None

def upload_to_github():
    print("\nStarting Cloud Sync...")
    try:
        repo = Repo(os.getcwd())
        
        # This is the 'Secret Sauce' fix:
        repo.git.add(OUTPUT_FILENAME) # Force adds the file via Git command line
        
        repo.index.commit("Design Update: Added Network Logos")
        
        origin = repo.remote(name='origin')
        remote_url = f"https://{GITHUB_USER}:{GITHUB_TOKEN}@github.com/{GITHUB_USER}/{REPO_NAME}.git"
        origin.set_url(remote_url)
        
        # Added 'force=True' here to prevent the 100644 error in the future
        origin.push(force=True)
        print("Success: GitHub is updated with Logos! 🚀")
    except Exception as e:
        print(f"Sync Error: {e}")

def run_filter():
    print(f"--- Running Pro M3U Filter + Logos ---")
    try:
        r = requests.get(SOURCE_URL, timeout=10)
        lines = r.text.splitlines()
        
        # Header with TV Guide link
        clean_list = ['#EXTM3U url-tvg="https://iptv-org.github.io/epg/guides/us.xml.gz"\n']
        
        for i in range(len(lines)):
            if "#EXTINF" in lines[i]:
                name = lines[i].split(",")[-1].strip()
                url = lines[i+1].strip()
                group = get_group(name)
                
                if group:
                    logo = get_logo_url(name)
                    # The 'Pro' line now includes group-title AND tvg-logo
                    pro_line = f'#EXTINF:-1 tvg-logo="{logo}" group-title="{group}",{name}'
                    clean_list.append(pro_line + "\n")
                    clean_list.append(url + "\n")

        with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
            f.writelines(clean_list)
        
        upload_to_github()

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_filter()

