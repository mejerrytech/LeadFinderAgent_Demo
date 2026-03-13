"""
Data Processor for handling lead data collection and processing
"""

import pandas as pd
import time
from api_client import APIClient
from scoring_engine import ScoringEngine
from config import Config


class DataProcessor:
    """Handles data collection, processing, and lead generation"""
    
    def __init__(self):
        self.api_client = APIClient()
        self.scoring_engine = ScoringEngine()
    
    def collect_barbershops(self):
        """
        Collect barbershop data from multiple search queries
        
        Returns:
            list: List of unique barbershop data
        """
        all_places = []
        seen_names = set()
        
        print("🔍 Searching for barbershops in Boston area...")
        
        for query in Config.SEARCH_QUERIES:
            print(f"Searching: {query}")
            places = self.api_client.search_barbershops(query)
            
            for place in places:
                name = place.get("title", "")
                
                # Avoid duplicates
                if name and name not in seen_names:
                    seen_names.add(name)
                    all_places.append(place)
            
            print(f"Found {len(all_places)} unique barbershops so far...")
            
            # Continue until we have enough or run out of queries
            if len(all_places) >= Config.TARGET_LEADS_COUNT and len(seen_names) >= Config.TARGET_LEADS_COUNT:
                break
            
            time.sleep(Config.RATE_LIMIT_DELAY)
        
        # Limit to target number
        return all_places[:Config.TARGET_LEADS_COUNT]
    
    def process_place_data(self, place):
        """
        Process individual place data and enrich with additional information
        
        Args:
            place (dict): Raw place data from API
            
        Returns:
            dict: Processed lead data
        """
        name = place.get("title")
        website = place.get("website", "")
        address = place.get("address")
        phone = place.get("phoneNumber")
        rating = place.get("rating", 0)
        reviews = place.get("ratingCount", 0)
        
        # Get Instagram data
        instagram = self.api_client.find_instagram(name)
        followers = self.api_client.get_instagram_followers(instagram)
        
        # Estimate barbers
        estimated_barbers = self.scoring_engine.estimate_barbers(reviews, rating)
        
        return {
            "Barbershop Name": name,
            "Website": website,
            "Address": address,
            "Phone": phone,
            "Instagram Link": instagram,
            "Instagram Followers": followers,
            "Google Rating": rating,
            "Google Reviews": reviews,
            "Estimated Barbers": estimated_barbers,
        }
    
    def generate_leads(self, places):
        """
        Generate leads from collected places data
        
        Args:
            places (list): List of place data
            
        Returns:
            list: List of processed lead data
        """
        leads = []
        
        for i, place in enumerate(places):
            print(f"\n[{i+1}/{len(places)}] Processing: {place.get('title')}")
            
            lead_data = self.process_place_data(place)
            leads.append(lead_data)
            
            time.sleep(Config.RATE_LIMIT_DELAY)
        
        return leads
    
    def calculate_scores_and_rank(self, df):
        """
        Calculate scores and rank the leads
        
        Args:
            df (pd.DataFrame): DataFrame with lead data
            
        Returns:
            pd.DataFrame: Ranked DataFrame with scores
        """
        # Calculate individual scores
        df["Instagram Score"] = df["Instagram Followers"].apply(self.scoring_engine.instagram_score)
        df["Review Score"] = df["Google Reviews"].apply(self.scoring_engine.review_score)
        df["Rating Score"] = df["Google Rating"].apply(self.scoring_engine.rating_score)
        df["Barber Score"] = df["Estimated Barbers"].apply(self.scoring_engine.barber_score)
        
        df["Social Score"] = df.apply(
            lambda x: self.scoring_engine.social_score(x["Website"], x["Instagram Link"]),
            axis=1
        )
        
        # Calculate total score
        df["Lead Score"] = df.apply(
            lambda x: self.scoring_engine.calculate_total_score(x),
            axis=1
        )
        
        # Sort by score and add rank
        df = df.sort_values(by="Lead Score", ascending=False)
        df["Lead Rank"] = range(1, len(df) + 1)
        
        # Add lead tier
        df["Lead Tier"] = df["Lead Score"].apply(self.scoring_engine.get_lead_tier)
        
        return df
    
    def export_to_csv(self, df, filename=None):
        """
        Export DataFrame to CSV
        
        Args:
            df (pd.DataFrame): DataFrame to export
            filename (str): Output filename
            
        Returns:
            str: Filename used
        """
        if filename is None:
            filename = Config.OUTPUT_FILENAME
            
        df.to_csv(filename, index=False)
        return filename
    
    def generate_summary_stats(self, df):
        """
        Generate summary statistics for the leads
        
        Args:
            df (pd.DataFrame): DataFrame with lead data
            
        Returns:
            dict: Summary statistics
        """
        return {
            "total_barbershops": len(df),
            "average_rating": df['Google Rating'].mean(),
            "average_reviews": df['Google Reviews'].mean(),
            "shops_with_instagram": len(df[df['Instagram Link'] != '']),
            "average_instagram_followers": df[df['Instagram Followers'] > 0]['Instagram Followers'].mean(),
            "tier_1_count": len(df[df['Lead Tier'] == 'Tier 1']),
            "tier_2_count": len(df[df['Lead Tier'] == 'Tier 2']),
            "tier_3_count": len(df[df['Lead Tier'] == 'Tier 3']),
        }
