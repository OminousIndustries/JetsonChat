# JetsonChat

An experimental chat application designed to run on NVIDIA Jetson devices using Ollama and small Llama3.2 models. This repository provides a simple implementation of an offline chatbot.

## Important Notes

- Ensure your sound settings are configured with the correct audio output and input devices before running the application.
- The Voice Activity Detection (VAD) may sometimes re-trigger when the LLM text-to-speech is playing. It's recommended to use a microphone with a mute button for better control.

## Installation

### 1. Install Python Dependencies

```bash
sudo apt install python3-pip -y
sudo apt install python3-venv -y
```

### 2. Create and Activate Virtual Environment

```bash
python3 -m venv ~/jetsonchat
source ~/jetsonchat/bin/activate
```

### 3. Install Ollama

Install Ollama using the official installation script:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 4. Run Ollama Model

Start the Ollama service and run the LLaMA model:

```bash
ollama run llama3.2:1b
ollama serve
```

### 5. Install JetsonChat

Clone the repository and install required Python packages:

```bash
git clone https://github.com/OminousIndustries/JetsonChat
cd JetsonChat
pip install -r requirements.txt
```

### 6. Run the Application

```bash
python main.py
```
