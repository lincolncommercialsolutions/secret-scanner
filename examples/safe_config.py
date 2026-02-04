"""
Safe configuration file - no secrets should be detected here.
"""

import os

# Good practice: Use environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
API_KEY = os.getenv("API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")

# Configuration without hardcoded secrets
class AppConfig:
    """Application configuration using environment variables."""
    
    def __init__(self):
        self.debug = os.getenv("DEBUG", "False") == "True"
        self.host = os.getenv("HOST", "localhost")
        self.port = int(os.getenv("PORT", "8000"))
    
    def get_database_url(self):
        """Get database URL from environment."""
        return os.getenv("DATABASE_URL", "sqlite:///app.db")
    
    def get_api_key(self):
        """Get API key from environment."""
        return os.getenv("API_KEY")


# Example of what looks like a secret but isn't
EXAMPLE_KEY_FORMAT = "AKIA followed by 16 characters"
PASSWORD_REQUIREMENTS = "must be at least 8 characters"

# Test data (clearly marked as test)
TEST_API_KEY = "test_key_for_testing_only"
MOCK_SECRET = "mock_secret_not_real"

print("This file uses best practices and should be safe")
