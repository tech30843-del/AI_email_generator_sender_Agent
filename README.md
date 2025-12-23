# 🤖 Email Agent - AI-Powered Email Assistant

An intelligent email agent that uses a local GGUF model (Mistral-7B) to automatically compose and send emails through Gmail API. The agent interacts conversationally, extracts recipient information, generates appropriate email content, and handles the entire email sending workflow.

## ✨ Features

- 🧠 **Local AI Model**: Uses Mistral-7B-Instruct (GGUF format) for email generation
- 📧 **Gmail Integration**: Automatic OAuth authentication and email sending via Gmail API
- 💬 **Conversational Interface**: Interactive CLI that guides you through email composition
- 🎯 **Smart Content Generation**: Automatically generates subject lines and email bodies
- 🔄 **Regeneration Option**: Don't like the generated email? Regenerate with one command
- 🔒 **Secure Authentication**: OAuth 2.0 token management with automatic refresh
- ⚡ **Sequential Workflow**: Step-by-step email creation process (recipient → subject → body → confirmation)

## 🎬 Demo

```
💬 You: Send an email to john@example.com about tomorrow's project meeting

🤖 Agent: [Generates email preview]
====================================================
📧 EMAIL PREVIEW
====================================================
To: john@example.com
Subject: Tomorrow's Project Meeting

Dear John,

I wanted to confirm our project meeting scheduled for tomorrow. 
Please let me know if the time still works for you.

Best regards
====================================================

🤖 Agent: Do you want to send this email? (yes/no/regenerate)
Your choice: yes

✅ Email sent successfully to john@example.com
```

## 📋 Requirements

### System Requirements
- Python 3.8 or higher
- At least 4GB RAM (for running the GGUF model)
- Windows/Linux/MacOS

### Python Libraries

```bash
# Core dependencies
llama-cpp-python>=0.2.0    # For GGUF model inference
google-api-python-client   # Gmail API
google-auth-oauthlib       # OAuth authentication
google-auth-httplib2       # Google auth helpers
smolagents                 # Agent framework (optional)
```

### AI Model

- **Model**: Mistral-7B-Instruct-v0.2 (GGUF format)
- **Quantization**: Q4_K_M (recommended for balance between speed and quality)
- **Size**: ~4GB
- **Download**: [TheBloke/Mistral-7B-Instruct-v0.2-GGUF](https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF)

### Gmail API Setup

You'll need Google Cloud credentials to use Gmail API:

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project (or select existing)
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Desktop app type)
5. Download the credentials as `credentials.json`

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/email-agent.git
cd email-agent
```

### 2. Install Dependencies

```bash
pip install llama-cpp-python google-api-python-client google-auth-oauthlib google-auth-httplib2 smolagents
```

**Note**: If you encounter issues with `llama-cpp-python`, you may need to install with specific flags:

```bash
# For CPU only
pip install llama-cpp-python

# For GPU support (CUDA)
CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python
```

### 3. Download the GGUF Model

Download Mistral-7B-Instruct-v0.2 GGUF model:

```bash
# Using wget (Linux/Mac)
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf

# Or download manually from:
# https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF
```

### 4. Configure Model Path

Update the model path in `agents_email_agent.py`:

```python
MODEL_PATH = r"path/to/your/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
```

### 5. Setup Gmail Credentials

1. Place your `credentials.json` (from Google Cloud Console) in the project directory
2. Update the sender email in `tools_send_email_gmail.py`:

```python
SENDER_EMAIL = "your-email@gmail.com"  # Replace with your Gmail address
```

### 6. First Run Authentication

On first run, the agent will:
- Open your browser for Gmail authorization
- Request permission to send emails
- Save the token for future use (no need to re-authenticate)

## 📖 Usage

### Basic Usage

```bash
python test_email_agent.py
```

### Example Interactions

**Example 1: Email with recipient in message**
```
💬 You: Send an email to sarah@company.com about the Q4 report deadline

[Agent generates and shows preview]
```

**Example 2: Email without recipient**
```
💬 You: Send a follow-up email about yesterday's discussion

🤖 Agent: Who should I send this email to? Please provide an email address.
💬 You: mike@team.com

[Agent generates and shows preview]
```

**Example 3: Regenerate email**
```
🤖 Agent: Do you want to send this email? (yes/no/regenerate)
Your choice: regenerate

[Agent generates a new version]
```

## 📁 Project Structure

```
email-agent/
│
├── agents_email_agent.py      # Main email agent logic
├── tools_send_email_gmail.py  # Gmail API integration
├── auth_manager.py            # OAuth token management
├── test_email_agent.py        # CLI interface
│
├── credentials.json           # Gmail OAuth credentials (not in repo)
├── token.json                 # Auto-generated auth token (not in repo)
│
└── mistral-7b-instruct-v0.2.Q4_K_M.gguf  # GGUF model (not in repo)
```

## 🔧 Configuration

### Model Parameters

Adjust in `agents_email_agent.py`:

```python
llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=4096,           # Context window size
    n_gpu_layers=0,       # Set to -1 for full GPU offload
    n_threads=6,          # CPU threads (adjust based on your system)
    verbose=False
)
```

### Generation Parameters

Modify in `LocalModelWrapper.generate()`:

```python
output = self.llm(
    prompt,
    max_tokens=200,       # Max length of generated text
    temperature=0.7,      # Randomness (0.0-1.0)
    top_p=0.95,          # Nucleus sampling
    stop=["</s>", "###", "\n\n\n"]
)
```

## ⚠️ Important Notes

### Security
- Never commit `credentials.json` or `token.json` to Git
- Add them to `.gitignore`
- Keep your OAuth credentials secure

### Gmail API Limitations
- Gmail API has sending limits (typically 500 emails/day for free accounts)
- Rate limiting may apply for frequent requests

### Model Performance
- First model load takes 10-30 seconds
- Generation speed depends on CPU/GPU
- Q4_K_M quantization balances quality and speed

## 🐛 Troubleshooting

### "Model not found" error
- Verify the `MODEL_PATH` in `agents_email_agent.py` is correct
- Ensure the GGUF file exists at the specified location

### "credentials.json not found"
- Download OAuth credentials from Google Cloud Console
- Place file in the project root directory

### "Token refresh failed"
- Delete `token.json` and re-authenticate
- Verify your OAuth credentials are still valid

### Slow generation
- Reduce `n_ctx` to 2048 or lower
- Use GPU offload if available (`n_gpu_layers=-1`)
- Consider using a smaller quantized model

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Mistral AI](https://mistral.ai/) for the Mistral-7B model
- [TheBloke](https://huggingface.co/TheBloke) for GGUF quantizations
- [llama.cpp](https://github.com/ggerganov/llama.cpp) for GGUF inference
- Google for Gmail API

## 📧 Contact

Your Name - [@yourtwitter](https://twitter.com/yourtwitter)

Project Link: [https://github.com/yourusername/email-agent](https://github.com/yourusername/email-agent)

---

⭐ If you find this project useful, please consider giving it a star on GitHub!
