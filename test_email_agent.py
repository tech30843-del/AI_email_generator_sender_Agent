"""
Email Agent Test with Automatic Authentication
Improved version with better formatting and user experience
"""

from agents_email_agent import EmailAgent
from tools_send_email_gmail import send_email_gmail, setup_gmail_auth

def print_separator(char="=", length=60):
    """Print a separator line"""
    print(char * length)

def print_email_preview(preview):
    """Print a nicely formatted email preview"""
    print_separator()
    print("📧 EMAIL PREVIEW")
    print_separator()
    print(f"To: {preview['receiver']}")
    print(f"Subject: {preview['subject']}")
    print()
    print(preview['body'])
    print_separator()

def main():
    print()
    print_separator()
    print("🤖 EMAIL AGENT - Starting...")
    print_separator()
    print()
    
    # Check authentication status
    print("→ Checking Gmail authentication...")
    try:
        if not setup_gmail_auth():
            print("\n✗ Authentication setup failed.")
            print("   Make sure credentials.json is in the current directory.")
            print("   Get it from: https://console.cloud.google.com")
            return
    except Exception as e:
        print(f"\n⚠ Authentication check failed: {e}")
        print("→ Will attempt authentication on first email send...\n")
    
    print()
    print_separator()
    print("✅ Ready to send emails!")
    print_separator()
    print()
    
    agent = EmailAgent()
    
    print("Email Agent started. Type 'quit' or 'exit' to close.\n")
    print("💡 Examples:")
    print("   • Send an email to john@example.com about project updates")
    print("   • Email sarah@company.com regarding tomorrow's meeting")
    print("   • Write to support@service.com about account issue")
    print()
    
    while True:
        try:
            user_input = input("\n💬 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!\n")
                break
            
            if not user_input:
                continue
            
            response = agent.process_step(user_input)
            
            if response["status"] == "need_receiver":
                print(f"\n🤖 Agent: {response['question']}")
                
            elif response["status"] == "need_clarification":
                print(f"\n🤖 Agent: {response['question']}")
                
            elif response["status"] == "confirmation":
                print()
                print_email_preview(response['email_preview'])
                
                # Store the body for regeneration
                agent.current_body = response['email_preview']['body']
                
                # Get confirmation
                print(f"\n🤖 Agent: {response['question']}")
                confirm = input("Your choice: ").strip().lower()
                
                result = agent.handle_confirmation(confirm)
                
                if result["status"] == "sent":
                    print(f"\n✅ {result['message']}")
                    
                elif result["status"] == "confirmation":
                    # Show regenerated email
                    print("\n🔄 Regenerated email:")
                    print_email_preview(result['email_preview'])
                    
                    # Store updated body
                    agent.current_body = result['email_preview']['body']
                    
                    # Ask again
                    print(f"\n🤖 Agent: {result['question']}")
                    confirm = input("Your choice: ").strip().lower()
                    
                    final = agent.handle_confirmation(confirm)
                    
                    if final["status"] == "sent":
                        print(f"\n✅ {final['message']}")
                    elif final["status"] == "cancelled":
                        print(f"\n❌ {final['message']}")
                    else:
                        print(f"\n→ {final['message']}")
                        
                elif result["status"] == "cancelled":
                    print(f"\n❌ {result['message']}")
                else:
                    print(f"\n→ {result['message']}")
            
            elif response["status"] == "error":
                print(f"\n❌ Error: {response['message']}")
                
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()