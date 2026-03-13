"""
Configuration settings for the Barbershop Lead Finder
"""

class Config:
    # API Configuration
    SERPER_API_KEY = "be108998fcee63c10ad3c1771ff7ab205d83e5d3"
    
    # Search Configuration
    DEFAULT_NUM_RESULTS = 50
    TARGET_LEADS_COUNT = 100
    RATE_LIMIT_DELAY = 1
    
    # Search Queries for Boston Area
    SEARCH_QUERIES = [
        "barbershops in Boston Massachusetts",
        "barber shop Boston MA", 
        "men's haircut Boston",
        "barbershop downtown Boston",
        "barbershop Cambridge MA",
        "barbershop Back Bay Boston",
        "barbershop South Boston",
        "barbershop North End Boston",
        "barbershop Beacon Hill Boston",
        "barbershop Fenway Boston",
        "barbershop Dorchester Boston",
        "barbershop Allston Boston",
        "barbershop Brighton Boston",
        "barbershop West End Boston",
        "barbershop Roxbury Boston",
        "barbershop Jamaica Plain Boston",
        "barbershop South End Boston",
        "barbershop Brookline MA",
        "barbershop Somerville MA",
        "barbershop Watertown MA"
    ]
    
    # Output Configuration
    OUTPUT_FILENAME = "boston_barbershop_leads_100.csv"
    
    # Scoring Thresholds
    INSTAGRAM_THRESHOLDS = {
        10000: 30,
        5000: 20,
        1000: 10,
        0: 5
    }
    
    REVIEW_THRESHOLDS = {
        300: 25,
        150: 20,
        50: 10,
        0: 5
    }
    
    RATING_THRESHOLDS = {
        4.6: 15,
        4.3: 12,
        4.0: 8,
        0: 5
    }
    
    BARBER_THRESHOLDS = {
        8: 20,
        5: 15,
        3: 10,
        0: 5
    }
    
    # API Headers
    API_HEADERS = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }
    
    # Browser Headers for Instagram
    BROWSER_HEADERS = {
        "User-Agent": "Mozilla/5.0"
    }
