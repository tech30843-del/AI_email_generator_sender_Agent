"""
Gmail send tool with built-in automatic token management.
No separate auth_manager.py file needed!
"""

from smolagents import tool
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Configuration
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"
SENDER_EMAIL = "*********@gmail.com"  # Replace with your Gmail address
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

# ============================================================
# Built-in Auth Manager (no separate file needed)
# ============================================================

class GmailAuthManager:
    def __init__(self, credentials_file, token_file):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.creds = None
    
    def get_credentials(self):
        """Get valid credentials, creating new ones if needed."""
        # Check if token exists and load it
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
        """Generate a new token via OAuth flow."""
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


# Global instance
_auth_manager = None

def get_auth_manager():
    """Get or create the global auth manager instance."""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = GmailAuthManager(CREDENTIALS_FILE, TOKEN_FILE)
    return _auth_manager


# ============================================================
# Email Sending Tool
# ============================================================

@tool
def send_email_gmail(to: str, subject: str, body: str) -> str:
    """
    Sends an email using the Gmail API with automatic authentication.
    On first run, will open browser for OAuth authorization.

    Args:
        to (str): The recipient's email address.
        subject (str): The subject line of the email.
        body (str): The plain text content of the email.

    Returns:
        str: A confirmation message containing the Gmail message ID.
    """
    try:
        # Get auth manager and credentials (handles OAuth automatically)
        auth_manager = get_auth_manager()
        creds = auth_manager.get_credentials()
        
        # Build Gmail service
        service = build("gmail", "v1", credentials=creds)
        
        # Create email message
        msg = MIMEText(body)
        msg["to"] = to
        msg["from"] = SENDER_EMAIL
        msg["subject"] = subject
        
        # Encode and send
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        result = service.users().messages().send(
            userId="me", 
            body={"raw": raw}
        ).execute()
        
        return f"✓ Email sent successfully to {to} (Message ID: {result['id']})"
        
    except FileNotFoundError as e:
        return str(e)
    except Exception as e:
        return f"✗ Failed to send email: {str(e)}"


def setup_gmail_auth():
    """
    Convenience function to setup Gmail authentication.
    
    Returns:
        bool: True if authentication successful, False otherwise
    """
    try:
        auth_manager = get_auth_manager()
        
        if auth_manager.is_authenticated():
            print("✓ Already authenticated")
            # Verify token is still valid
            creds = auth_manager.get_credentials()
            print("✓ Token is valid")
            return True
        else:
            print("→ Starting authentication process...")
            creds = auth_manager.get_credentials()
            print("✓ Authentication complete!")
            return True
            
    except Exception as e:
        print(f"✗ Authentication failed: {e}")

        return False
