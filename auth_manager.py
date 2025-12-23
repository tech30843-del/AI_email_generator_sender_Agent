"""
Automatic Gmail OAuth Token Manager
Handles token creation, refresh, and validation automatically.

Save this file as: auth_manager.py
Place it in the same directory as your other code files.
"""

import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

class GmailAuthManager:
    def __init__(self, credentials_file="credentials.json", token_file="token.json"):
        """
        Initialize the auth manager.
        
        Args:
            credentials_file: Path to OAuth credentials from Google Cloud Console
            token_file: Path where token will be stored/loaded
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.creds = None
    
    def get_credentials(self):
        """
        Get valid credentials, creating new ones if needed.
        This method handles the entire OAuth flow automatically.
        
        Returns:
            Valid Google OAuth credentials
        """
        # Check if token.json exists and load it
        if os.path.exists(self.token_file):
            try:
                self.creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
                print(f"✓ Loaded existing token from {self.token_file}")
            except Exception as e:
                print(f"⚠ Error loading token: {e}")
                self.creds = None
        
        # If credentials don't exist or are invalid
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                # Token expired but can be refreshed
                print("⟳ Refreshing expired token...")
                try:
                    self.creds.refresh(Request())
                    print("✓ Token refreshed successfully")
                except Exception as e:
                    print(f"⚠ Token refresh failed: {e}")
                    print("→ Generating new token...")
                    self.creds = self._generate_new_token()
            else:
                # No valid credentials, need to generate new token
                self.creds = self._generate_new_token()
            
            # Save the credentials for next time
            self._save_token()
        
        return self.creds
    
    def _generate_new_token(self):
        """
        Generate a new token via OAuth flow.
        Opens browser for user authorization.
        """
        if not os.path.exists(self.credentials_file):
            raise FileNotFoundError(
                f"\n{'='*60}\n"
                f"ERROR: {self.credentials_file} not found!\n\n"
                f"To fix this:\n"
                f"1. Go to Google Cloud Console (console.cloud.google.com)\n"
                f"2. Enable Gmail API for your project\n"
                f"3. Create OAuth 2.0 credentials (Desktop app)\n"
                f"4. Download the credentials JSON file\n"
                f"5. Save it as '{self.credentials_file}' in this directory\n"
                f"{'='*60}\n"
            )
        
        print("\n" + "="*60)
        print("🔐 FIRST TIME SETUP - Gmail OAuth Authorization")
        print("="*60)
        print(f"→ Opening browser for authorization...")
        print(f"→ Please log in and grant access to send emails")
        print(f"→ This only needs to be done once\n")
        
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_file, 
                SCOPES
            )
            creds = flow.run_local_server(port=0)
            print("\n✓ Authorization successful!")
            return creds
        except Exception as e:
            print(f"\n✗ Authorization failed: {e}")
            raise
    
    def _save_token(self):
        """Save credentials to token file"""
        try:
            with open(self.token_file, 'w') as f:
                f.write(self.creds.to_json())
            print(f"✓ Token saved to {self.token_file}")
        except Exception as e:
            print(f"⚠ Failed to save token: {e}")
    
    def is_authenticated(self):
        """Check if user is already authenticated"""
        return os.path.exists(self.token_file)


# Singleton instance for easy access
_auth_manager = None

def get_auth_manager(credentials_file="credentials.json", token_file="token.json"):
    """
    Get or create the global auth manager instance.
    
    Args:
        credentials_file: Path to credentials.json
        token_file: Path to token.json
    
    Returns:
        GmailAuthManager instance
    """
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = GmailAuthManager(credentials_file, token_file)
    return _auth_manager