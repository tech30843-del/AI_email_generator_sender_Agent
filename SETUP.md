# 🔧 Detailed Setup Guide

This guide provides step-by-step instructions for setting up the Email Agent project.

## Table of Contents

1. [Google Cloud Setup](#google-cloud-setup)
2. [Model Download](#model-download)
3. [Python Environment](#python-environment)
4. [Configuration](#configuration)
5. [First Run](#first-run)

---

## Google Cloud Setup

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click on the project dropdown at the top
3. Click "New Project"
4. Enter a project name (e.g., "Email Agent")
5. Click "Create"

### Step 2: Enable Gmail API

1. In the left sidebar, go to **APIs & Services → Library**
2. Search for "Gmail API"
3. Click on "Gmail API"
4. Click the "Enable" button

### Step 3: Configure OAuth Consent Screen

1. Go to **APIs & Services → OAuth consent screen**
2. Select "External" user type
3. Click "Create"
4. Fill in the required fields:
   - **App name**: Email Agent
   - **User support email**: Your email
   - **Developer contact**: Your email
5. Click "Save and Continue"
6. On "Scopes" page, click "Add or Remove Scopes"
7. Search and add: `https://www.googleapis.com/auth/gmail.send`
8. Click "Update" and then "Save and Continue"
9. On "Test users" page, add your Gmail address
10. Click "Save and Continue"

### Step 4: Create OAuth Credentials

1. Go to **APIs & Services → Credentials**
2. Click "Create Credentials" → "OAuth client ID"
3. Select "Desktop app" as application type
4. Enter a name (e.g., "Email Agent Desktop")
5. Click "Create"
6. A dialog will appear with your credentials
7. Click "Download JSON"
8. Rename the downloaded file to `credentials.json`
9. Move it to your project directory

---

## Model Download

### Option 1: Direct Download (Recommended)

1. Go to [Mistral-7B-Instruct-v0.2-GGUF](https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF)
2. Find the file: `mistral-7b-instruct-v0.2.Q4_K_M.gguf`
3. Click to download (~4GB)
4. Place it in your project directory

### Option 2: Command Line (Linux/Mac)

```bash
cd /path/to/email-agent
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf
```

### Option 3: Using Hugging Face CLI

```bash
pip install huggingface-hub

huggingface-cli download TheBloke/Mistral-7B-Instruct-v0.2-GGUF \
  mistral-7b-instruct-v0.2.Q4_K_M.gguf \
  --local-dir ./
```

---

## Python Environment

### Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate

# On Linux/Mac:
source venv/bin/activate
```

### Install Dependencies

```bash
# Install all requirements
pip install -r requirements.txt
```

### Verify Installation

```bash
python -c "from llama_cpp import Llama; print('llama-cpp-python: OK')"
python -c "import googleapiclient; print('Google API: OK')"
```

---

## Configuration

### 1. Update Model Path

Edit `agents_email_agent.py`:

```python
# Change this line to your model location
MODEL_PATH = r"C:\path\to\mistral-7b-instruct-v0.2.Q4_K_M.gguf"

# Examples:
# Windows: MODEL_PATH = r"C:\Users\YourName\email-agent\mistral-7b-instruct-v0.2.Q4_K_M.gguf"
# Linux:   MODEL_PATH = "/home/yourname/email-agent/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
# Mac:     MODEL_PATH = "/Users/yourname/email-agent/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
```

### 2. Update Sender Email

Edit `tools_send_email_gmail.py`:

```python
# Change this line to your Gmail address
SENDER_EMAIL = "your-email@gmail.com"
```

### 3. Verify Files Structure

Your project directory should look like:

```
email-agent/
├── agents_email_agent.py
├── tools_send_email_gmail.py
├── auth_manager.py
├── test_email_agent.py
├── requirements.txt
├── credentials.json                    ← From Google Cloud
├── mistral-7b-instruct-v0.2.Q4_K_M.gguf  ← Downloaded model
└── README.md
```

---

## First Run

### 1. Start the Agent

```bash
python test_email_agent.py
```

### 2. Initial Load

You'll see:
```
Loading GGUF model... This may take a few seconds...
Model loaded successfully.
```

This can take 10-30 seconds on first run.

### 3. OAuth Authentication

On first run, the agent will:

1. Check for authentication
2. Open your browser automatically
3. Ask you to log in to Gmail
4. Request permission to send emails
5. Save the token for future use

Follow the browser prompts:
- Select your Gmail account
- Click "Continue" on the permissions screen
- Grant access to "Send email on your behalf"

### 4. Success!

You should see:
```
✅ Authentication complete!
✅ Ready to send emails!

Email Agent started. Type 'quit' or 'exit' to close.
```

---

## Testing

### Test Command

Try this to verify everything works:

```
💬 You: Send a test email to yourself@gmail.com about project setup

[Agent will generate and show preview]
Your choice: yes

✅ Email sent successfully!
```

### Check Your Inbox

1. Open Gmail
2. Look for the email you just sent
3. Verify it arrived correctly

---

## Troubleshooting

### Issue: "credentials.json not found"

**Solution**: 
- Download OAuth credentials from Google Cloud Console
- Rename to exactly `credentials.json`
- Place in project root directory

### Issue: "Model loading failed"

**Solutions**:
- Verify model path is correct
- Check file exists and is not corrupted (should be ~4GB)
- Try re-downloading the model
- Ensure enough RAM (need at least 4GB free)

### Issue: "Token refresh failed"

**Solutions**:
- Delete `token.json`
- Run the agent again to re-authenticate
- Verify Google Cloud credentials are still valid
- Check OAuth consent screen is properly configured

### Issue: "Permission denied" during OAuth

**Solutions**:
- Verify your email is added as a test user in Google Cloud Console
- Make sure Gmail API is enabled
- Check OAuth consent screen configuration
- Try creating new OAuth credentials

### Issue: Slow model inference

**Solutions**:
- Reduce context window: change `n_ctx=4096` to `n_ctx=2048`
- Use GPU acceleration if available: set `n_gpu_layers=-1`
- Consider using a smaller quantization (Q3_K_M)
- Increase CPU threads: adjust `n_threads` to match your CPU cores

---

## Advanced Configuration

### Using GPU Acceleration

If you have an NVIDIA GPU:

```bash
# Uninstall CPU version
pip uninstall llama-cpp-python

# Install with CUDA support
CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python
```

Then in `agents_email_agent.py`:

```python
llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=4096,
    n_gpu_layers=-1,  # Offload all layers to GPU
    n_threads=6,
    verbose=False
)
```

### Custom Model Parameters

Experiment with these in `LocalModelWrapper.generate()`:

```python
output = self.llm(
    prompt,
    max_tokens=200,      # Length: 100-500
    temperature=0.7,     # Creativity: 0.1-1.0 (lower = more focused)
    top_p=0.95,         # Diversity: 0.5-1.0
    repeat_penalty=1.1,  # Reduce repetition
    stop=["</s>", "###", "\n\n\n"]
)
```

---

## Security Best Practices

### 1. Protect Credentials

```bash
# Add to .gitignore
echo "credentials.json" >> .gitignore
echo "token.json" >> .gitignore
```

### 2. Token Storage

- `token.json` is auto-generated and should NOT be shared
- It contains refresh tokens for your Gmail account
- Delete it to revoke access

### 3. OAuth Scopes

Current scope: `gmail.send` (send emails only)

To expand capabilities, add more scopes in `tools_send_email_gmail.py`:

```python
SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    # "https://www.googleapis.com/auth/gmail.readonly",  # Read emails
    # "https://www.googleapis.com/auth/gmail.modify",    # Modify emails
]
```

---

## Getting Help

If you encounter issues:

1. Check this guide first
2. Review error messages carefully
3. Search existing GitHub issues
4. Open a new issue with:
   - Error message
   - Steps to reproduce
   - System info (OS, Python version)

---

**Happy emailing! 📧**
