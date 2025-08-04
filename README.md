# Mental Health Chatbot with Sentiment Analysis

## Project Overview
This project is a web-based **Mental Health Chatbot** designed to provide initial emotional support by analyzing user input sentiment using natural language processing (NLP). The chatbot leverages a pre-trained DistilBERT model to classify user messages as positive, negative, or neutral, offering tailored responses and suggesting professional resources for negative sentiments. Built with Flask and a simple HTML/CSS/JavaScript frontend, it serves as a proof-of-concept for AI-driven mental health support tools.

### Features
- **Sentiment Analysis**: Uses Hugging Face's DistilBERT model to analyze user input sentiment.
- **Dynamic Responses**: Provides context-aware replies based on detected sentiment (positive, negative, neutral).
- **Resource Suggestions**: Offers mental health resources (e.g., helplines, websites) for negative sentiments with high confidence (>70%).
- **Interactive UI**: A responsive web interface with scrollable chat history and sentiment feedback.
- **Extensible**: Modular design allows for additional features like mood tracking or multilingual support.

## Prerequisites
- **Python**: Version 3.8 or higher.
- **Web Browser**: Chrome, Firefox, or any modern browser.
- **Internet Connection**: Required for initial model download from Hugging Face.
- **Dependencies**:
  - Flask (`pip install flask`)
  - Transformers (`pip install transformers`)
  - PyTorch (`pip install torch`)

## Installation
1. **Clone or Download the Project**:
   - Clone the repository or download the project files (`chatbot.py`, `templates/index.html`).
   - Ensure the `index.html` file is placed in a `templates` folder in the same directory as `chatbot.py`.

2. **Set Up a Virtual Environment** (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
