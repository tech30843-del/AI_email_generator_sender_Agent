import json
import re
from llama_cpp import Llama
from tools_send_email_gmail import send_email_gmail

# ============================================================
# GGUF MODEL PATH
# ============================================================
MODEL_PATH = r"C:\Users\DELL PRO\Desktop\email_agent\mistral-7b-instruct-v0.2.Q4_K_M.gguf"
print("Loading GGUF model... This may take a few seconds...")

llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=4096,
    n_gpu_layers=0,  # CPU only
    n_threads=6,
    verbose=False
)

print("Model loaded successfully.")

# ============================================================
# Wrapper for the model
# ============================================================
class LocalModelWrapper:
    def __init__(self, llm):
        self.llm = llm

    def generate(self, prompt: str, max_tokens=512) -> str:
        """Return plain text from model."""
        output = self.llm(
            prompt,
            max_tokens=max_tokens,
            temperature=0.7,
            top_p=0.95,
            stop=["</s>", "###", "\n\n\n"]  # Added triple newline as stop
        )
        return output["choices"][0]["text"].strip()

local_model = LocalModelWrapper(llm)

# ============================================================
# Email Agent (Sequential Approach)
# ============================================================
class EmailAgent:
    def __init__(self, model=local_model):
        self.model = model
        self.current_receiver = None
        self.current_subject = None
        self.current_body = None
        self.original_request = None
        self.waiting_for = None  # 'receiver', 'clarification', or None

    def extract_email_from_text(self, text):
        """Extract email using regex pattern"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, text)
        return matches[0] if matches else None

    def _clean_response(self, text):
        """Clean model response from code and explanations"""
        if not text:
            return ""
        # Remove code blocks
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        # Remove function definitions
        text = re.sub(r'def\s+\w+\(.*?\):', '', text)
        # Remove technical explanations
        text = re.sub(r'#.*', '', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text.strip()

    def _generate_subject(self, request):
        """Generate clear subject using strict JSON output parsing"""
        
        subject_prompt = f"""
        Extract a short, clear email subject from this request.
        Return ONLY JSON: {{"subject": "clear subject here"}}
        
        Rules:
        - Maximum 6-8 words
        - Professional and clear
        - No explanations, no code
        - Just the subject text
        
        Request: {request}
        JSON:
        """

        raw = self.model.generate(subject_prompt).strip()
        
        # Try to capture JSON
        subject = ""
        try:
            json_match = re.search(r'\{[^}]*\}', raw)
            if json_match:
                data = json.loads(json_match.group())
                subject = data.get("subject", "").strip()
        except:
            subject = ""

        subject = self._clean_response(subject)
        
        # LENIENT VALIDATION - avoid loop at all costs
        if subject and len(subject) >= 3:
            return subject

        # ---- FALLBACK 1: Direct generation ----
        fallback_prompt = f"Very short email subject for: {request}"
        fallback = self.model.generate(fallback_prompt).strip()
        fallback = self._clean_response(fallback)
        
        if fallback and len(fallback) >= 3:
            return fallback

        # ---- FALLBACK 2: Ultra-simple ----
        ultra_simple = self.model.generate(f"2-3 word topic for: {request}").strip()
        ultra_simple = self._clean_response(ultra_simple)
        
        if ultra_simple and len(ultra_simple) >= 2:
            return ultra_simple

        # ---- FINAL FALLBACK: Guaranteed no loop ----
        return "Follow Up"
    
    def _generate_body(self):
        """Generate clean, short email body without placeholders"""
        # Extract first name from email
        receiver_name = self.current_receiver.split('@')[0].split('.')[0].title()
        
        body_prompt = f"""Write a SHORT professional email body (2-3 sentences maximum).

REQUEST: {self.original_request}
SUBJECT: {self.current_subject}
RECEIVER: {receiver_name}

RULES:
- Start with greeting: "Dear {receiver_name},"
- Write ONLY 2-3 sentences about the request
- End with: "Best regards"
- NO extra information, NO placeholders, NO contact info
- Keep it brief and focused

EMAIL:"""

        # Generate with shorter token limit
        body = self.model.generate(body_prompt, max_tokens=200)
        body = self._clean_email_body(body, receiver_name)
        
        return body

    def _clean_email_body(self, text, receiver_name):
        """Enhanced cleaning to fix double greeting and extra content"""
        if not text:
            return ""
        
        # Remove any repeated subject lines
        text = re.sub(r'^Subject:.*?\n', '', text, flags=re.IGNORECASE | re.MULTILINE)
        text = re.sub(r'^Re:.*?\n', '', text, flags=re.IGNORECASE | re.MULTILINE)
        
        # Remove all placeholder brackets and their content
        text = re.sub(r'\[.*?\]', '', text)
        
        # Remove contact information sections
        text = re.sub(r'Your Contact Information.*?$', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'Email.*?:.*?\n', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Phone.*?:.*?\n', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Website.*?:.*?\n', '', text, flags=re.IGNORECASE)
        
        # Remove job title lines
        text = re.sub(r'^Your Job Title.*?\n', '', text, flags=re.IGNORECASE | re.MULTILINE)
        
        # Clean up excessive newlines (more than 2 consecutive)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        # Check if greeting already exists
        has_greeting = bool(re.search(r'^(Dear|Hello|Hi|Greetings)\s+\w+', text, re.IGNORECASE))
        
        # Only add greeting if it doesn't exist
        if not has_greeting:
            text = f"Dear {receiver_name},\n\n{text}"
        
        # Check if closing already exists
        has_closing = bool(re.search(r'(Best regards|Regards|Sincerely|Thank you|Best)\s*$', text, re.IGNORECASE | re.MULTILINE))
        
        # Only add closing if it doesn't exist
        if not has_closing:
            # Make sure text ends with proper punctuation
            if not text.endswith(('.', '!', '?')):
                text += '.'
            text += "\n\nBest regards"
        
        # Final cleanup: remove any lines that are just dashes or equals signs
        lines = text.split('\n')
        cleaned_lines = [line for line in lines if not re.match(r'^[-=_]{3,}$', line.strip())]
        text = '\n'.join(cleaned_lines)
        
        # Remove any duplicate consecutive lines
        lines = text.split('\n')
        final_lines = []
        prev_line = None
        for line in lines:
            if line.strip() != prev_line:
                final_lines.append(line)
            prev_line = line.strip()
        text = '\n'.join(final_lines)
        
        return text.strip()

    def process_step(self, user_input: str):
        """
        Process step by step:
        1. First get receiver
        2. Then generate subject from request
        3. If subject unclear, ask for clarification
        4. Then generate body
        """
        
        # If we're waiting for receiver
        if self.waiting_for == 'receiver':
            receiver = self.extract_email_from_text(user_input)
            if receiver:
                self.current_receiver = receiver
                self.waiting_for = None
                # Now generate subject from the original request
                return self._generate_subject_step()
            else:
                return {
                    "status": "need_receiver",
                    "question": "That doesn't look like a valid email address. Please provide a proper email address."
                }
        
        # If we're waiting for clarification
        elif self.waiting_for == 'clarification':
            # Use the NEW input as the request to generate subject
            self.original_request = user_input
            self.waiting_for = None
            return self._generate_subject_step()
        
        # Initial step - no receiver yet
        elif self.current_receiver is None:
            receiver = self.extract_email_from_text(user_input)
            if receiver:
                self.current_receiver = receiver
                self.original_request = user_input
                return self._generate_subject_step()
            else:
                self.original_request = user_input
                self.waiting_for = 'receiver'
                return {
                    "status": "need_receiver",
                    "question": "Who should I send this email to? Please provide an email address."
                }
        
        # Should not reach here
        else:
            return {"status": "error", "message": "Unexpected state"}

    def _generate_subject_step(self):
        """Try to generate subject and proceed accordingly"""
        subject = self._generate_subject(self.original_request)
        
        if subject:
            self.current_subject = subject
            return self._generate_final_email()
        else:
            self.waiting_for = 'clarification'
            return {
                "status": "need_clarification",
                "question": "I'm not sure what this email should be about. Could you please clarify the purpose or topic?"
            }

    def _generate_final_email(self):
        """Generate the final email with body"""
        body = self._generate_body()
        self.current_body = body
        
        return {
            "status": "confirmation",
            "email_preview": {
                "receiver": self.current_receiver,
                "subject": self.current_subject,
                "body": body
            },
            "question": "Do you want to send this email? (yes/no/regenerate)"
        }

    def handle_confirmation(self, user_response: str):
        """Handle user confirmation response"""
        if user_response.lower() in ['yes', 'y', 'send']:
            # Send the email
            result = send_email_gmail(
                self.current_receiver,
                self.current_subject,
                self.current_body
            )
            self._reset()
            return {"status": "sent", "message": result}
        
        elif user_response.lower() in ['regenerate', 'r']:
            # Regenerate body only
            body = self._generate_body()
            self.current_body = body
            return {
                "status": "confirmation",
                "email_preview": {
                    "receiver": self.current_receiver,
                    "subject": self.current_subject,
                    "body": body
                },
                "question": "Do you want to send this email? (yes/no/regenerate)"
            }
        
        else:  # no or any other response
            self._reset()
            return {"status": "cancelled", "message": "Email discarded."}

    def _reset(self):
        """Reset the agent state"""
        self.current_receiver = None
        self.current_subject = None
        self.current_body = None
        self.original_request = None
        self.waiting_for = None