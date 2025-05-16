from flask import Flask, request, render_template_string, send_file, redirect, url_for
import os
from openai import AzureOpenAI
from azure.identity import ClientSecretCredential, get_bearer_token_provider
from datetime import datetime
import re

app = Flask(__name__, static_folder='.', static_url_path='')  
app.secret_key = 'your_secret_key_here'  # Change to a strong, random secret key

# --- Configure Azure OpenAI and Cognitive Search ---
endpoint = os.getenv("ENDPOINT_URL", "https://grmopenaidemo.openai.azure.com/")
deployment = os.getenv("DEPLOYMENT_NAME", "gpt-4o")

# Replace these with your actual credentials or set them as environment variables
client_id = '5ca1e9c3-ca28-4cf4-824a-7400ae8bf334'
tenant_id = 'b6ad3b74-02d8-4bab-a4fb-1b6607a159b9'
description = 'Chatbot-AI-App-Secret'
client_secret = 'eRh8Q~5HrQaL6._jF_zinAT9AHhe49a5Nz4p_ar2'
secret = '63d2de8e-39f5-4c9e-9cad-c27bd57b629a'
ai_key = 'C5CrN8ERJGDt8uC2hZ4qx7Fb9YBdcVBiEu5gGADTdB5Q1CeQbpyfJQQJ99BDAC77bzfXJ3w3AAABACOG44jL'

# Create a credential using a service principal
credential = ClientSecretCredential(
    tenant_id=tenant_id,
    client_id=client_id,
    client_secret=client_secret
)
cognitiveServicesResource = "https://cognitiveservices.azure.com"
token_provider = get_bearer_token_provider(
    credential, 
    f'{cognitiveServicesResource}/.default'
)

client = AzureOpenAI(  
    azure_endpoint=endpoint,  
    azure_ad_token_provider=token_provider,  
    api_version='2024-05-01-preview',
)


# ---------------------- Utility: current timestamp ----------------------
def current_time():
    """Returns the current time in a user-friendly format (e.g., '10:05 AM')."""
    return datetime.now().strftime("%I:%M %p")

# ---------------------- Conversation History ----------------------
# Each message stored as: { "role": "assistant" or "user", "content": "...", "timestamp": "..." }
conversation_history = [
    {
        "role": "assistant",
        "content": "Hello! How can I assist you today?",
        "timestamp": current_time()
    }
]

# ---------------------- Chatbot Response Function ----------------------
def get_chatbot_response(user_message):
    """
    Appends the user's message to the conversation history, calls the Azure OpenAI service,
    and appends the assistant's response (with timestamp) to the history.
    """
    global conversation_history
    conversation_history.append({
        "role": "user",
        "content": user_message,
        "timestamp": current_time()
    })
    
    # Prepare conversation for API (filter out timestamps)
    conversation_for_api = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in conversation_history
    ]
    
    response = client.chat.completions.create(
        model=deployment,
        messages=conversation_for_api,
        max_tokens=800,
        temperature=0.7,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        extra_body={
            "data_sources": [
                {
                    "type": "azure_search",
                    "parameters": {
                        "endpoint": os.getenv("AZURE_SEARCH_ENDPOINT", "https://azureaisearchgrm.search.windows.net"),
                        "index_name": "knowledge-index",
                        "authentication": {
                            "type": "api_key",
                            "key": os.getenv("AZURE_SEARCH_ADMIN_KEY", "3UWafBL3qfK5gkomj1diHKvmK8RVZ6lGgIDHJLkB1sAzSeAbH6uW")
                        }
                    }
                }
            ]
        }
    )
    assistant_message = response.choices[0].message.content

    # 1) Remove references like [doc1], [doc2], etc.
    assistant_message = re.sub(r"\[doc\d+\]", "", assistant_message)

    # 2) Remove unnecessary spaces before periods:
    #    e.g. turns "Ravindra Talwai ." into "Ravindra Talwai."
    assistant_message = re.sub(r"\s+\.", ".", assistant_message)

    # 3) Remove any extra whitespace
    assistant_message = re.sub(r"\s+", " ", assistant_message).strip()

    conversation_history.append({
        "role": "assistant",
        "content": assistant_message,
        "timestamp": current_time()
    })
    return assistant_message

CHATBOT_TEMPLATE = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>GradientM Chatbot</title>
    <!-- Modern sans-serif font -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">

    <style>
      /* Remove default margins/padding and ensure full height */
      html, body {
        margin: 0;
        padding: 0;
        height: 100%;
        font-family: 'Inter', sans-serif;
      }
      /* Make the chat fill the entire viewport */
      body {
        display: flex;
        justify-content: center;
        align-items: center;
        background-color: #f2f2f2; /* or any background you prefer */
      }
      .chat-container {
        width: 100vw;
        height: 100vh;
        display: flex;
        flex-direction: column;
        background: #ffffff;
        /* If you don't want a border, remove or adjust below: */
        /* border: 1px solid #ddd; */
        /* border-radius: 8px; */
        /* box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); */
        overflow: hidden;
      }
      /* Chat Header */
      .chat-header {
        background: #ffffff;
        border-bottom: 1px solid #e0e0e0;
        padding: 16px;
        text-align: center;
        font-weight: 600;
        font-size: 1.3rem;
        position: relative;
      }
      /* "Clear Chat" link or button if needed */
      .clear-chat-btn {
        position: absolute;
        right: 16px;
        top: 50%;
        transform: translateY(-50%);
        background: transparent;
        border: none;
        color: #3f51b5;
        font-size: 0.9rem;
        cursor: pointer;
        text-decoration: underline;
      }
      .clear-chat-btn:hover { color: #5c6bc0; }

      /* Loading Indicator at the top (hidden by default) */
      .loading-indicator {
        display: none; /* hidden unless "Send" is clicked */
        width: 100%;
        height: 4px;
        background: linear-gradient(to right, #4A90E2, #76c7c0, #4A90E2);
        background-size: 200% auto;
        animation: loading-progress 1.5s linear infinite;
      }
      @keyframes loading-progress {
        0% {
          background-position: 0% center;
        }
        100% {
          background-position: 200% center;
        }
      }

      /* Chat messages scrollable area */
      .chat-messages {
        flex: 1;
        padding: 16px;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 12px;
        scrollbar-width: thin;
      }
      .chat-messages::-webkit-scrollbar {
        width: 6px;
      }
      .chat-messages::-webkit-scrollbar-track {
        background: #f0f0f0;
      }
      .chat-messages::-webkit-scrollbar-thumb {
        background-color: #ccc;
        border-radius: 4px;
      }

      /* Message bubbles */
      .message {
        display: flex;
        flex-direction: column;
        max-width: 80%;
      }
      .message.assistant {
        align-self: flex-start;
      }
      .message.user {
        align-self: flex-end;
        text-align: right;
      }
      .bubble {
        padding: 12px 16px;
        border-radius: 8px;
        background: #f1f1f1;
        animation: fadeIn 0.3s ease-in-out forwards;
        word-wrap: break-word;
      }
      .message.user .bubble {
        background: #e7f0fd;
      }
      @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to   { opacity: 1; transform: translateY(0); }
      }
      /* Timestamps below each bubble */
      .timestamp {
        font-size: 0.75rem;
        color: #999;
        margin-top: 4px;
      }

      /* Chat input area */
      .chat-input {
        display: flex;
        border-top: 1px solid #e0e0e0;
        padding: 16px;
        gap: 8px;
        background: #ffffff;
      }
      .chat-input input[type="text"] {
        flex: 1;
        padding: 12px 16px;
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        font-size: 1rem;
        transition: background-color 0.2s ease-in-out;
      }
      .chat-input input[type="text"]::placeholder { color: #999; }
      .chat-input input[type="text"]:focus {
        background-color: #f2f2f2;
      }
      .chat-input button {
        background-color: #3f51b5;
        border: none;
        border-radius: 4px;
        padding: 12px 16px;
        font-size: 1rem;
        color: #fff;
        cursor: pointer;
        transition: background-color 0.3s ease-in-out, transform 0.1s ease-in-out;
      }
      .chat-input button:hover { background-color: #5c6bc0; }
      .chat-input button:active { transform: scale(0.98); }

      /* Mobile / Smaller Screens */
      @media (max-width: 480px) {
        .chat-header {
          font-size: 1rem;
          padding: 12px;
        }
        .chat-input {
          padding: 12px;
        }
        .chat-input input[type="text"] {
          padding: 10px 12px;
        }
        .chat-input button {
          padding: 10px 14px;
        }
      }
    </style>
  </head>
  <body>
    <!-- Container for everything -->
    <div class="chat-container">

      <!-- Chat Header + Clear Button -->
      <div class="chat-header">
        GradientM Chatbot
        <a href="/reset" class="clear-chat-btn">Clear</a>
      </div>

      <!-- Loading Bar (hidden by default) -->
      <div id="loadingIndicator" class="loading-indicator"></div>

      <!-- Messages -->
      <div class="chat-messages">
        {% for msg in conversation %}
          <div class="message {{ msg.role }}">
            <div class="bubble">{{ msg.content }}</div>
            <div class="timestamp">{{ msg.timestamp }}</div>
          </div>
        {% endfor %}
      </div>

      <!-- Input Form -->
      <form action="/chat" method="post" class="chat-input" onsubmit="showLoader()">
        <input type="text" name="question" placeholder="Type your question..." required autofocus>
        <button type="submit">Send</button>
      </form>
    </div>

    <!-- Minimal JavaScript to show the loader when user clicks "Send" -->
    <script>
      function showLoader() {
        document.getElementById('loadingIndicator').style.display = 'block';
      }
    </script>
  </body>
</html>
"""


# ---------------------- Chatbot Routes ----------------------
@app.route('/chat', methods=["GET", "POST"])
def chat():
    if request.method == "POST":
        user_question = request.form.get("question")
        get_chatbot_response(user_question)
        return redirect(url_for('chat'))
    return render_template_string(CHATBOT_TEMPLATE, conversation=conversation_history)

# ---------------------- Main Company Site Route ----------------------
@app.route('/')
def home():
    return send_file("index.html")

# ---------------------- Reset Conversation Endpoint ----------------------
@app.route('/reset', methods=["GET"])
def reset():
    global conversation_history
    conversation_history = [{
        "role": "assistant",
        "content": "Hello! How can I assist you today?",
        "timestamp": current_time()
    }]
    return redirect(url_for('chat'))

if __name__ == "__main__":
    app.run(debug=True)