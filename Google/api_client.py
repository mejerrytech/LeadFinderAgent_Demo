"""
API Client for handling external API calls
"""

import requests
import time
from bs4 import BeautifulSoup
from config import Config


class APIClient:
    """Handles all external API interactions"""
    
    def __init__(self):
        self.headers = Config.API_HEADERS
        self.browser_headers = Config.BROWSER_HEADERS
    
    def search_barbershops(self, query, num_results=None):
        """
        Search for barbershops using Serper Places API
        
        Args:
            query (str): Search query
            num_results (int): Number of results to return
            
        Returns:
            list: List of place data
        """
        if num_results is None:
            num_results = Config.DEFAULT_NUM_RESULTS
            
        url = "https://google.serper.dev/places"
        
        payload = {
            "q": query,
            "gl": "us",
            "hl": "en",
            "num": num_results
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("places", [])
        except requests.RequestException as e:
            print(f"Error searching barbershops: {e}")
            return []
    
    def find_instagram(self, name):
        """
        Find Instagram profile for a business name
        
        Args:
            name (str): Business name to search for
            
        Returns:
            str: Instagram URL or empty string
        """
        payload = {
            "q": f'site:instagram.com "{name}" Boston barber',
            "num": 5
        }
        
        try:
            response = requests.post(
                "https://google.serper.dev/search",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            if "organic" in data:
                for result in data["organic"]:
                    link = result.get("link", "")
                    if "instagram.com" in link and "/p/" not in link:
                        return link
        except requests.RequestException as e:
            print(f"Error finding Instagram for {name}: {e}")
        
        return ""
    
    def get_instagram_followers(self, url):
        """
        Extract follower count from Instagram profile
        
        Args:
            url (str): Instagram profile URL
            
        Returns:
            int: Number of followers
        """
        if not url:
            return 0
        
        try:
            response = requests.get(url, headers=self.browser_headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "lxml")
            meta = soup.find("meta", property="og:description")
            
            if meta:
                text = meta.get("content", "")
                # Example: "12.5K Followers, 120 Following, 210 Posts"
                followers = text.split("Followers")[0]
                followers = followers.replace(",", "").strip()
                
                if "K" in followers:
                    followers = float(followers.replace("K", "")) * 1000
                elif "M" in followers:
                    followers = float(followers.replace("M", "")) * 1000000
                
                return int(float(followers))
        except Exception as e:
            print(f"Error getting Instagram followers from {url}: {e}")
        
        return 0
