"""
Boston Barbershop Lead Finder - Main Application
A sophisticated lead generation and scoring system for Boston barbershops
"""

import pandas as pd
from data_processor import DataProcessor
from config import Config


class LeadFinder:
    """Main application class for lead generation"""
    
    def __init__(self):
        self.processor = DataProcessor()
    
    def run(self):
        """Run the complete lead generation process"""
        print("🚀 Starting Boston Barbershop Lead Generation...")
        print(f"🎯 Target: {Config.TARGET_LEADS_COUNT} qualified leads")
        print("=" * 60)
        
        # Step 1: Collect barbershop data
        places = self.processor.collect_barbershops()
        print(f"✅ Total unique barbershops found: {len(places)}")
        
        if not places:
            print("❌ No barbershops found. Please check your API configuration.")
            return
        
        # Step 2: Generate leads with enriched data
        print(f"\n🔄 Processing {len(places)} barbershops...")
        leads = self.processor.generate_leads(places)
        
        # Step 3: Create DataFrame and calculate scores
        print("\n📊 Calculating lead scores and rankings...")
        df = pd.DataFrame(leads)
        ranked_df = self.processor.calculate_scores_and_rank(df)
        
        # Step 4: Export results
        filename = self.processor.export_to_csv(ranked_df)
        print(f"\n🎉 SUCCESS! Generated {len(ranked_df)} barbershop leads")
        print(f"📁 File saved as: {filename}")
        
        # Step 5: Display summary
        self.display_summary(ranked_df)
        
        return ranked_df
    
    def display_summary(self, df):
        """Display summary statistics and top leads"""
        stats = self.processor.generate_summary_stats(df)
        
        print("\n📊 SUMMARY:")
        print(f"Total barbershops: {stats['total_barbershops']}")
        print(f"Average rating: {stats['average_rating']:.1f}")
        print(f"Average reviews: {stats['average_reviews']:.0f}")
        print(f"Shops with Instagram: {stats['shops_with_instagram']}")
        print(f"Average Instagram followers: {stats['average_instagram_followers']:.0f}")
        
        print(f"\n🏆 LEAD DISTRIBUTION:")
        print(f"Tier 1 (80-100 pts): {stats['tier_1_count']} shops")
        print(f"Tier 2 (50-79 pts): {stats['tier_2_count']} shops") 
        print(f"Tier 3 (0-49 pts): {stats['tier_3_count']} shops")
        
        print("\n🏆 TOP 10 LEADS:")
        top_10 = df.head(10)
        for _, row in top_10.iterrows():
            print(f"{row['Lead Rank']}. {row['Lead Score']}pts ({row['Lead Tier']}) - {row['Barbershop Name']}")
            print(f"   ⭐ {row['Google Rating']} ({row['Google Reviews']} reviews)")
            if row['Instagram Followers'] > 0:
                print(f"   📷 {row['Instagram Followers']:,} followers")
            print()
        
        print(f"✅ Lead file generated: {Config.OUTPUT_FILENAME}")


def main():
    """Main entry point"""
    try:
        lead_finder = LeadFinder()
        results = lead_finder.run()
        return results
    except KeyboardInterrupt:
        print("\n⏹️  Process interrupted by user")
        return None
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None


if __name__ == "__main__":
    main()