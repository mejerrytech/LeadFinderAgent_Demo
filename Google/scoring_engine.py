"""
Scoring Engine for lead evaluation and ranking
"""

import random
from config import Config


class ScoringEngine:
    """Handles all scoring logic and lead evaluation"""
    
    @staticmethod
    def instagram_score(followers):
        """Calculate Instagram score based on follower count"""
        thresholds = Config.INSTAGRAM_THRESHOLDS
        
        if followers >= 10000:
            return thresholds[10000]
        elif followers >= 5000:
            return thresholds[5000]
        elif followers >= 1000:
            return thresholds[1000]
        elif followers > 0:
            return thresholds[0]
        return 0
    
    @staticmethod
    def review_score(reviews):
        """Calculate review score based on review count"""
        thresholds = Config.REVIEW_THRESHOLDS
        
        if reviews >= 300:
            return thresholds[300]
        elif reviews >= 150:
            return thresholds[150]
        elif reviews >= 50:
            return thresholds[50]
        elif reviews > 0:
            return thresholds[0]
        return 0
    
    @staticmethod
    def rating_score(rating):
        """Calculate rating score based on Google rating"""
        thresholds = Config.RATING_THRESHOLDS
        
        if rating >= 4.6:
            return thresholds[4.6]
        elif rating >= 4.3:
            return thresholds[4.3]
        elif rating >= 4.0:
            return thresholds[4.0]
        elif rating > 0:
            return thresholds[0]
        return 0
    
    @staticmethod
    def barber_score(barbers):
        """Calculate barber score based on estimated number of barbers"""
        thresholds = Config.BARBER_THRESHOLDS
        
        if barbers >= 8:
            return thresholds[8]
        elif barbers >= 5:
            return thresholds[5]
        elif barbers >= 3:
            return thresholds[3]
        elif barbers > 0:
            return thresholds[0]
        return 0
    
    @staticmethod
    def social_score(website, instagram):
        """Calculate social presence score"""
        if website and instagram:
            return 10
        elif instagram:
            return 5
        return 0
    
    @staticmethod
    def estimate_barbers(reviews, rating):
        """
        Estimate number of barbers based on reviews and rating
        
        Args:
            reviews (int): Number of Google reviews
            rating (float): Google rating
            
        Returns:
            int: Estimated number of barbers
        """
        if reviews >= 500:
            return random.randint(6, 10)
        elif reviews >= 200:
            return random.randint(4, 7)
        elif reviews >= 50:
            return random.randint(2, 5)
        else:
            return random.randint(1, 3)
    
    @staticmethod
    def calculate_total_score(df_row):
        """
        Calculate total lead score for a barbershop
        
        Args:
            df_row: Pandas DataFrame row with all data
            
        Returns:
            int: Total lead score
        """
        instagram_score = ScoringEngine.instagram_score(df_row['Instagram Followers'])
        review_score = ScoringEngine.review_score(df_row['Google Reviews'])
        rating_score = ScoringEngine.rating_score(df_row['Google Rating'])
        barber_score = ScoringEngine.barber_score(df_row['Estimated Barbers'])
        social_score = ScoringEngine.social_score(df_row['Website'], df_row['Instagram Link'])
        
        return instagram_score + review_score + rating_score + barber_score + social_score
    
    @staticmethod
    def get_lead_tier(score):
        """
        Determine lead tier based on score
        
        Args:
            score (int): Lead score
            
        Returns:
            str: Lead tier (Tier 1, Tier 2, Tier 3)
        """
        if score >= 80:
            return "Tier 1"
        elif score >= 50:
            return "Tier 2"
        else:
            return "Tier 3"
