from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import asyncio
import re

app = FastAPI()

# Helper function to handle common misspellings
def correct_misspelling(message: str) -> str:
    corrections = {
        "timing": "time",
        "attractin": "attraction",
        "adress": "address",
        "resarant": "restaurant",
        "tiket": "ticket"
    }
    for wrong, correct in corrections.items():
        message = re.sub(rf"\b{wrong}\b", correct, message)
    return message

# Hardcoded responses for the chatbot
def chatbot_response(message: str) -> str:
    # Correct misspellings first
    message = correct_misspelling(message.lower())

    # Basic greetings
    if "hello" in message or "hi" in message:
        return "Hello! How can I assist you today?"
    elif "good morning" in message:
        return "Good morning! How can I help you today?"
    elif "good evening" in message:
        return "Good evening! What can I assist you with today?"
    elif "thank you" in message or "thanks" in message:
        return "You're welcome! I'm here if you need further assistance."
    
    # Wonderla-specific queries
    if "ticket" in message:
        return "Our ticket prices start from ₹1000 for adults and ₹800 for children. Visit our website for more details."
    elif "timing" in message or "open" in message:
        return "We are open from 10 AM to 6 PM on weekdays and from 10 AM to 7 PM on weekends."
    elif "attraction" in message or "ride" in message:
        return ("We have a variety of attractions including roller coasters, water slides, and a Ferris wheel! "
                "Don't miss out on the Rain Disco and the Wave Pool. Visit the website for a full list.")
    elif "location" in message or "address" in message:
        return "We have locations in Bengaluru, Kochi, and Hyderabad. Visit our website for directions!"
    elif "water park" in message:
        return "Our water park includes exciting rides like the Wave Pool, Lazy River, and Rain Disco!"
    elif "food" in message or "restaurant" in message:
        return ("We offer a variety of delicious meals, including both vegetarian and non-vegetarian options at our restaurants. "
                "Enjoy a relaxing meal after a fun-filled day!")
    elif "offer" in message or "deal" in message:
        return ("Current offers include: Funtastic Four (buy 3 tickets, get 1 free), Women’s Wednesdays (Buy 2 Get 2 Free), "
                "and 10% off for early birds when booking 3 days in advance! Visit our website for more details.")
    elif "help" in message:
        return "I’m here to help! You can ask me about ticket prices, timings, attractions, locations, and more!"
    else:
        return "I'm not sure about that. You can visit the official Wonderla website for more information."

# HTML for the chatbot client interface
html = """
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Wonderla Helpcenter Chatbot</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: linear-gradient(45deg, #1a1a1d, #4e4e50, #22536f);
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                color: white;
            }
            .chat-container {
                width: 100%;
                max-width: 600px;
                background-color: #222;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
                border-radius: 10px;
                display: flex;
                flex-direction: column;
                height: 80vh;
                border: 1px solid #076595;
            }
            .chat-header {
                background: linear-gradient(45deg, #225b6f, #22536f);
                color: white;
                padding: 15px;
                text-align: center;
                font-size: 24px;
                border-bottom: 1px solid #070d95;
            }
            .chat-messages {
                flex: 1;
                padding: 20px;
                overflow-y: auto;
                background-color: #333;
            }
            .chat-messages ul {
                list-style: none;
                padding: 0;
                color: white;
            }
            .chat-messages ul li {
                padding: 10px;
                margin-bottom: 10px;
                background-color: #224d6f;
                border-radius: 5px;
                max-width: 80%;
                word-wrap: break-word;
                font-family: 'Courier New', Courier, monospace;
            }
            .chat-messages ul li.you {
                background-color: #076e95;
                text-align: right;
            }
            .chat-footer {
                display: flex;
                padding: 10px;
                background-color: #444;
                border-top: 1px solid #6f2232;
            }
            .chat-footer input {
                flex: 1;
                padding: 10px;
                font-size: 16px;
                border: 1px solid #076595;
                border-radius: 5px;
                background-color: #555;
                color: white;
                margin-right: 10px;
            }
            .chat-footer button {
                padding: 10px 15px;
                font-size: 16px;
                background-color: #073a95;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                transition: background-color 0.3s;
            }
            .chat-footer button:hover {
                background-color: #6f2232;
            }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <div class="chat-header">Wonderla Bot</div>
            <div class="chat-messages">
                <ul id="messages"></ul>
            </div>
            <div class="chat-footer">
                <input type="text" id="messageText" placeholder="Type your message..." autocomplete="off" />
                <button onclick="sendMessage()">Send</button>
            </div>
        </div>

        <script>
            const ws = new WebSocket("ws://wonderlabot.onrender.com/ws");

            ws.onmessage = function(event) {
                setTimeout(function() {
                    var messages = document.getElementById('messages');
                    var message = document.createElement('li');
                    message.textContent = "Chatbot: " + event.data;
                    messages.appendChild(message);
                    messages.scrollTop = messages.scrollHeight;
                }, 1000);  // Delay for chatbot response (1 second)
            };

            function sendMessage() {
                var input = document.getElementById("messageText");
                if (input.value.trim() !== "") {
                    var messages = document.getElementById('messages');
                    var message = document.createElement('li');
                    message.classList.add("you");
                    message.textContent = "You: " + input.value;
                    messages.appendChild(message);
                    ws.send(input.value);
                    input.value = '';
                    messages.scrollTop = messages.scrollHeight;
                }
            }

            document.getElementById("messageText").addEventListener("keypress", function(event) {
                if (event.key === "Enter") {
                    sendMessage();
                }
            });
        </script>
    </body>
</html>
"""

# WebSocket manager to handle connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        # Send a greeting message when a new connection is established
        await websocket.send_text("Welcome to Wonderla Helpcenter! How can I assist you today?")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# Serve the chatbot HTML interface at the root URL
@app.get("/", response_class=HTMLResponse)
async def get():
    return html

# WebSocket endpoint for real-time chat
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await asyncio.sleep(1)  # Add delay for realistic response time
            response = chatbot_response(data)
            await manager.send_personal_message(response, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
