import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
import re

# Configuration
SERPER_API_KEY = "be108998fcee63c10ad3c1771ff7ab205d83e5d3"
REQUEST_TIMEOUT = 5
RATE_LIMIT_DELAY = 2

# -----------------------------
# INSTAGRAM FUNCTIONS
# -----------------------------

def find_instagram(business_name):
    """Find Instagram account for a business"""
    try:
        query = f"{business_name} barbershop Boston Instagram"
        url = "https://google.serper.dev/search"
        
        payload = {
            "q": query,
            "num": 5
        }
        
        headers = {
            "X-API-KEY": SERPER_API_KEY,
            "Content-Type": "application/json"
        }
        
        r = requests.post(url, json=payload, headers=headers)
        data = r.json()
        
        for result in data.get("organic", []):
            link = result.get("link", "")
            if "instagram.com" in link:
                print(f"Found Instagram for {business_name}: {link}")
                return link
                
    except Exception as e:
        print(f"Error finding Instagram: {e}")
    
    return None

def get_instagram_followers(instagram_url):

    if not instagram_url:
        return 0

    if "/p/" in instagram_url:
        return 0

    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
        }

        r = requests.get(instagram_url, headers=headers, timeout=10)
        html = r.text

        # Extract JSON data from page
        shared_data = re.search(r'window\._sharedData = (.*?);</script>', html)

        if shared_data:
            data = json.loads(shared_data.group(1))

            user = data["entry_data"]["ProfilePage"][0]["graphql"]["user"]

            followers = user["edge_followed_by"]["count"]

            print(f"Real followers for {instagram_url}: {followers}")

            return followers

        # Backup method using meta tag
        soup = BeautifulSoup(html, "html.parser")

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
        print("Instagram scraping error:", e)

    return 0

# -----------------------------
# SCORING FUNCTIONS
# -----------------------------

def instagram_score(f):
    if f is None or pd.isna(f):
        return 0
    f = int(f)
    if f >= 10000:
        return 30
    elif f >= 5000:
        return 20
    elif f >= 1000:
        return 10
    elif f > 0:
        return 5
    return 0

def review_score(r):
    if r is None or pd.isna(r):
        return 0
    r = int(r)
    if r >= 300:
        return 25
    elif r >= 150:
        return 20
    elif r >= 50:
        return 10
    elif r > 0:
        return 5
    return 0

def rating_score(r):
    if r is None or pd.isna(r):
        return 0
    r = float(r)
    if r >= 4.6:
        return 15
    elif r >= 4.3:
        return 12
    elif r >= 4.0:
        return 8
    elif r > 0:
        return 5
    return 0

def barber_score(b):
    if b is None or pd.isna(b):
        return 0
    b = int(b)
    if b >= 8:
        return 20
    elif b >= 5:
        return 15
    elif b >= 3:
        return 10
    elif b > 0:
        return 5
    return 0

def social_score(site, insta):
    if (site is None or pd.isna(site)) and (insta is None or pd.isna(insta)):
        return 0
    elif (site is not None and not pd.isna(site)) and (insta is not None and not pd.isna(insta)):
        return 10
    elif insta is not None and not pd.isna(insta):
        return 5
    return 0

# -----------------------------
# STEP 1: GET YELP URLS
# -----------------------------

def get_yelp_links():

    url = "https://google.serper.dev/search"

    payload = {
        "q": 'site:yelp.com/biz barbershop "Boston MA"',
        "num": 20
    }

    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }

    r = requests.post(url, json=payload, headers=headers)
    data = r.json()

    businesses = []

    for result in data.get("organic", []):
        link = result.get("link")
        
        if "yelp.com/biz" in link:
            # Extract data directly from API response
            name = result.get("title", "").replace(" Photos - Yelp", "").replace(" - Updated March 2026 - Yelp", "").replace(" - Boston, Massachusetts - Yelp", "").replace(" - Yelp", "").strip()
            rating = result.get("rating")
            reviews = result.get("ratingCount")
            snippet = result.get("snippet", "")
            
            # Extract phone - look for pattern (xxx) xxx-xxxx
            phone = None
            if "(" in snippet and ")" in snippet:
                start = snippet.find("(")
                end = snippet.find(")", start) + 8  # Include area code and next 7 digits
                if end <= len(snippet):
                    phone = snippet[start:end].strip()
            
            # Extract address - look for street address pattern
            address = None
            # Split by comma and look for address parts
            parts = snippet.split(",")
            for part in parts:
                part = part.strip()
                # Check if it starts with a number (street address)
                if part and part[0].isdigit() and ("St" in part or "Ave" in part or "St." in part):
                    address = part
                    break
            
        

            businesses.append({
                "Name": name,
                "Rating": rating,
                "Reviews": reviews,
                "Phone": phone,
                "Address": address,
                "Yelp URL": link
            })

    return businesses


# -----------------------------
# STEP 2: SCRAPE BUSINESS PAGE
# -----------------------------

def scrape_yelp(url):

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    name = None
    rating = None
    reviews = None
    phone = None
    address = None

    # Business name
    title = soup.find("h1")
    if title:
        name = title.text.strip()

    # Rating
    rating_tag = soup.find("div", {"role": "img"})
    if rating_tag:
        rating_text = rating_tag.get("aria-label", "")
        if "star rating" in rating_text:
            rating = rating_text.split(" ")[0]

    # Reviews
    review_tag = soup.find("span", string=lambda s: s and "review" in s.lower())
    if review_tag:
        reviews = review_tag.text.split(" ")[0]


    # Address
    address_tag = soup.find("address")
    if address_tag:
        address = address_tag.text.strip()

    return {
        "Name": name,
        "Rating": rating,
        "Reviews": reviews,
        "Address": address,
        "Yelp URL": url
    }


# -----------------------------
# STEP 3: PIPELINE
# -----------------------------

def main():

    print("Finding Yelp barbershops...")

    businesses = get_yelp_links()

    print(f"Found {len(businesses)} barbershops\n")

    leads = []

    for business in businesses:

        name = business["Name"]
        print(f"Processing: {name}")

        # Get Instagram information
        instagram = find_instagram(name)
        followers = get_instagram_followers(instagram)

        # Estimate barbers (placeholder - could be improved)
        estimated_barbers = 3

        leads.append({
            "Barbershop Name": name,
            "Address": business["Address"],
            "Phone": business["Phone"],
            "Instagram Link": instagram,
            "Instagram Followers": followers,
            "Google Rating": business["Rating"],
            "Google Reviews": business["Reviews"],
            "Estimated Barbers": estimated_barbers,

            "Yelp URL": business["Yelp URL"]
        })

        time.sleep(2)  # Rate limiting

    df = pd.DataFrame(leads)

    # -----------------------------
    # CALCULATE SCORES
    # -----------------------------

    df["Instagram Score"] = df["Instagram Followers"].apply(instagram_score)
    df["Review Score"] = df["Google Reviews"].apply(review_score)
    df["Rating Score"] = df["Google Rating"].apply(rating_score)
    df["Barber Score"] = df["Estimated Barbers"].apply(barber_score)
    df["Social Score"] = df.apply(
        lambda x: social_score("", x["Instagram Link"]), 
        axis=1
    )

    df["Lead Score"] = (
        df["Instagram Score"]
        + df["Review Score"]
        + df["Rating Score"]
        + df["Barber Score"]
        + df["Social Score"]
    )

    # -----------------------------
    # RANK LEADS
    # -----------------------------

    df = df.sort_values(by="Lead Score", ascending=False)
    df["Lead Rank"] = range(1, len(df) + 1)

    # -----------------------------
    # FINAL COLUMN ORDER
    # -----------------------------

    df = df[
        [
            "Lead Rank",
            "Barbershop Name",
            "Address",
            "Phone",
            "Instagram Link",
            "Instagram Followers",
            "Google Rating",
            "Google Reviews",
            "Review Score",
            "Estimated Barbers",
            "Lead Score",
            "Yelp URL"
        ]
    ]

    # -----------------------------
    # EXPORT
    # -----------------------------

    df.to_csv("boston_barbers_yelp_scored.csv", index=False)

    print(f"\nSaved {len(df)} scored barbershops to boston_barbers_yelp_scored.csv")
    
    # Display top 5 leads
    print("\nTop 5 Leads:")
    for i, (_, lead) in enumerate(df.head(5).iterrows()):
        print(f"\n{lead['Lead Rank']}. {lead['Barbershop Name']}")
        print(f"   Score: {lead['Lead Score']}")
        print(f"   Rating: {lead['Google Rating']} ({lead['Google Reviews']} reviews)")
        print(f"   Instagram: {lead['Instagram Followers']} followers")
        print(f"   Phone: {lead['Phone']}")
        print(f"   Address: {lead['Address']}")
      


if __name__ == "__main__":
    main()