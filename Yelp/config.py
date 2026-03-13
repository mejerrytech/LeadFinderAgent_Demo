"""
Configuration settings for Boston Barbershop Lead Generation
"""

# API Configuration
SERPER_API_KEY = "be108998fcee63c10ad3c1771ff7ab205d83e5d3"
REQUEST_TIMEOUT = 5
RATE_LIMIT_DELAY = 2

# Search Configuration
SEARCH_QUERY = 'site:yelp.com/biz barbershop "Boston MA"'
NUM_RESULTS = 20
INSTAGRAM_SEARCH_NUM = 5

# File Paths
OUTPUT_FILE = "boston_barbers_yelp_scored.csv"

# Scoring Thresholds
INSTAGRAM_THRESHOLDS = {
    "very_high": 10000,
    "high": 5000,
    "medium": 1000
}

REVIEW_THRESHOLDS = {
    "very_high": 300,
    "high": 150,
    "medium": 50
}

RATING_THRESHOLDS = {
    "excellent": 4.6,
    "good": 4.3,
    "average": 4.0
}

BARBER_THRESHOLDS = {
    "large": 8,
    "medium": 5,
    "small": 3
}
