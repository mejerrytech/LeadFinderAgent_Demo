"""
Main application for Boston Barbershop Lead Generation
"""

import time
import pandas as pd
from config import RATE_LIMIT_DELAY, OUTPUT_FILE
from data_extractor import DataExtractor
from instagram_extractor import InstagramExtractor
from scoring_engine import ScoringEngine


class LeadGenerator:
    """Main lead generation application"""
    
    def __init__(self):
        self.data_extractor = DataExtractor()
        self.instagram_extractor = InstagramExtractor()
        self.scoring_engine = ScoringEngine()
    
    def run(self):
        """Execute the complete lead generation pipeline"""
        print("🔍 Finding Boston Barbershops...")
        
        # Step 1: Get Yelp businesses
        businesses = self.data_extractor.get_yelp_businesses()
        print(f"✅ Found {len(businesses)} barbershops\n")
        
        # Step 2: Process each business
        leads = []
        
        for i, business in enumerate(businesses, 1):
            print(f"📊 Processing {i}/{len(businesses)}: {business['Name']}")
            
            # Get Instagram data
            instagram = self.data_extractor.find_instagram(business["Name"])
            followers = self.instagram_extractor.extract_followers(instagram)
            
            # Create lead record
            lead = {
                "Barbershop Name": business["Name"],
                "Address": business["Address"],
                "Phone": business["Phone"],
                "Instagram Link": instagram,
                "Instagram Followers": followers,
                "Google Rating": business["Rating"],
                "Google Reviews": business["Reviews"],
                "Estimated Barbers": 3,  # Default estimate
                "Yelp URL": business["Yelp URL"]
            }
            
            leads.append(lead)
            time.sleep(RATE_LIMIT_DELAY)  # Rate limiting
        
        # Step 3: Score leads
        df = pd.DataFrame(leads)
        df = self._apply_scoring(df)
        
        # Step 4: Rank and export
        df = self._rank_leads(df)
        self._export_results(df)
        self._display_top_leads(df)
    
    def _apply_scoring(self, df):
        """Apply all scoring functions to DataFrame"""
        print("📈 Calculating lead scores...")
        
        df["Instagram Score"] = df["Instagram Followers"].apply(self.scoring_engine.instagram_score)
        df["Review Score"] = df["Google Reviews"].apply(self.scoring_engine.review_score)
        df["Rating Score"] = df["Google Rating"].apply(self.scoring_engine.rating_score)
        df["Barber Score"] = df["Estimated Barbers"].apply(self.scoring_engine.barber_score)
        df["Social Score"] = df.apply(
            lambda x: self.scoring_engine.social_score("", x["Instagram Link"]),
            axis=1
        )
        
        # Calculate total score
        df["Lead Score"] = (
            df["Instagram Score"] +
            df["Review Score"] +
            df["Rating Score"] +
            df["Barber Score"] +
            df["Social Score"]
        )
        
        return df
    
    def _rank_leads(self, df):
        """Rank leads by score"""
        print("🏆 Ranking leads...")
        
        df = df.sort_values(by="Lead Score", ascending=False)
        df["Lead Rank"] = range(1, len(df) + 1)
        
        return df
    
    def _export_results(self, df):
        """Export results to CSV"""
        print("💾 Exporting results...")
        
        # Define final column order
        final_columns = [
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
        
        df = df[final_columns]
        df.to_csv(OUTPUT_FILE, index=False)
        
        print(f"✅ Saved {len(df)} scored barbershops to {OUTPUT_FILE}")
    
    def _display_top_leads(self, df):
        """Display top 5 leads"""
        print("\n🌟 Top 5 Leads:")
        print("=" * 50)
        
        for _, lead in df.head(5).iterrows():
            print(f"\n{lead['Lead Rank']}. {lead['Barbershop Name']}")
            print(f"   📊 Score: {lead['Lead Score']}")
            print(f"   ⭐ Rating: {lead['Google Rating']} ({lead['Google Reviews']} reviews)")
            print(f"   📷 Instagram: {lead['Instagram Followers']} followers")
            print(f"   📞 Phone: {lead['Phone']}")
            print(f"   📍 Address: {lead['Address']}")


def main():
    """Main entry point"""
    app = LeadGenerator()
    app.run()


if __name__ == "__main__":
    main()
