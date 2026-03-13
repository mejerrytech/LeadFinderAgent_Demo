"""
Instagram follower extraction module
"""

import requests
import json
import re
from bs4 import BeautifulSoup
from config import REQUEST_TIMEOUT


class InstagramExtractor:
    """Handles Instagram follower count extraction"""
    
    @staticmethod
    def extract_followers(instagram_url):
        """
        Extract follower count from Instagram profile
        
        Args:
            url (str): Instagram profile URL
            
        Returns:
            int: Number of followers
        """
        if not instagram_url:
            return 0
        
        # Check if it's a profile URL (not a post URL)
        if "/p/" in instagram_url:
            return 0  # Post URLs don't have follower counts
        
        try:
            headers = {
                "User-Agent": "Mozilla/5.0",
            }
            
            response = requests.get(instagram_url, headers=headers, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            # Method 1: Extract JSON data from page
            shared_data = re.search(r'window\._sharedData = (.*?);</script>', response.text)
            
            if shared_data:
                data = json.loads(shared_data.group(1))
                user = data["entry_data"]["ProfilePage"][0]["graphql"]["user"]
                followers = user["edge_followed_by"]["count"]
                
                print(f"Real followers for {instagram_url}: {followers}")
                return followers
            
            # Method 2: Backup using meta tag
            soup = BeautifulSoup(response.text, "html.parser")
            meta = soup.find("meta", property="og:description")
            
            if meta:
                content = meta.get("content", "")
                match = re.search(r'([\d,.]+[KM]?) Followers', content)
                
                if match:
                    followers_text = match.group(1).replace(",", "")
                    
                    if "K" in followers_text:
                        followers = int(float(followers_text.replace("K","")) * 1000)
                    elif "M" in followers_text:
                        followers = int(float(followers_text.replace("M","")) * 1000000)
                    else:
                        followers = int(followers_text)
                    
                    print(f"Followers extracted: {followers}")
                    return followers
                    
        except Exception as e:
            print(f"Instagram scraping error: {e}")
            
        return 0
