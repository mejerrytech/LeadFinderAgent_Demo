"""
Lead scoring engine for barbershop evaluation
"""

import pandas as pd
from config import (
    INSTAGRAM_THRESHOLDS, 
    REVIEW_THRESHOLDS, 
    RATING_THRESHOLDS, 
    BARBER_THRESHOLDS
)


class ScoringEngine:
    """Handles all lead scoring calculations"""
    
    @staticmethod
    def instagram_score(followers):
        """Calculate Instagram follower score"""
        if followers is None or pd.isna(followers):
            return 0
        
        followers = int(followers)
        
        if followers >= INSTAGRAM_THRESHOLDS["very_high"]:
            return 30
        elif followers >= INSTAGRAM_THRESHOLDS["high"]:
            return 20
        elif followers >= INSTAGRAM_THRESHOLDS["medium"]:
            return 10
        elif followers > 0:
            return 5
        return 0
    
    @staticmethod
    def review_score(reviews):
        """Calculate review count score"""
        if reviews is None or pd.isna(reviews):
            return 0
        
        reviews = int(reviews)
        
        if reviews >= REVIEW_THRESHOLDS["very_high"]:
            return 25
        elif reviews >= REVIEW_THRESHOLDS["high"]:
            return 20
        elif reviews >= REVIEW_THRESHOLDS["medium"]:
            return 10
        elif reviews > 0:
            return 5
        return 0
    
    @staticmethod
    def rating_score(rating):
        """Calculate rating score"""
        if rating is None or pd.isna(rating):
            return 0
        
        rating = float(rating)
        
        if rating >= RATING_THRESHOLDS["excellent"]:
            return 15
        elif rating >= RATING_THRESHOLDS["good"]:
            return 12
        elif rating >= RATING_THRESHOLDS["average"]:
            return 8
        elif rating > 0:
            return 5
        return 0
    
    @staticmethod
    def barber_score(barbers):
        """Calculate barber count score"""
        if barbers is None or pd.isna(barbers):
            return 0
        
        barbers = int(barbers)
        
        if barbers >= BARBER_THRESHOLDS["large"]:
            return 20
        elif barbers >= BARBER_THRESHOLDS["medium"]:
            return 15
        elif barbers >= BARBER_THRESHOLDS["small"]:
            return 10
        elif barbers > 0:
            return 5
        return 0
    
    @staticmethod
    def social_score(website, instagram):
        """Calculate social media presence score"""
        if (website is None or pd.isna(website)) and (instagram is None or pd.isna(instagram)):
            return 0
        elif (website is not None and not pd.isna(website)) and (instagram is not None and not pd.isna(instagram)):
            return 10
        elif instagram is not None and not pd.isna(instagram):
            return 5
        return 0
