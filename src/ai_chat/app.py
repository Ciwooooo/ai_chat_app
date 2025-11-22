"""FastAPI web application for AI Chat.

This module contains the main web application including:
- HTML chat interface
- Form handling for chat messages
- API endpoint for programmatic access
- Health check for Kubernetes probes
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from jinja2 import Template
from pydantic import BaseModel

from ai_chat.chat import chat_completion
from ai_chat.config import settings


# ---------------------------------------------------------------------------
# Conversation Storage
# ---------------------------------------------------------------------------
# Store conversation history in memory (simple approach)
# In production, you might use Redis, a database, or session storage
conversation_history: list[dict[str, str]] = []


# ---------------------------------------------------------------------------
# HTML Template
# ---------------------------------------------------------------------------
# Embedded HTML template for the chat interface
# Using inline template keeps the app self-contained (no external files needed)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        /* Reset and base styles */
        * { 
            box-sizing: border-box; 
            margin: 0; 
            padding: 0; 
        }
        
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #eee; 
            min-height: 100vh; 
            display: flex; 
            flex-direction: column; 
        }
        
        /* Main container */
        .container { 
            max-width: 900px; 
            margin: 0 auto; 
            padding: 20px; 
            flex: 1; 
            display: flex; 
            flex-direction: column;
            width: 100%;
        }
        
        /* Header */
        h1 { 
            text-align: center; 
            margin-bottom: 20px; 
            color: #00d9ff;
            font-size: 2rem;
        }
        
        /* Chat messages container */
        .chat-box { 
            flex: 1; 
            overflow-y: auto; 
            border: 1px solid #333; 
            border-radius: 12px; 
            padding: 20px; 
            margin-bottom: 15px; 
            background: rgba(22, 33, 62, 0.8);
            min-height: 400px;
            max-height: 60vh;
        }
        
        /* Individual message */
        .message { 
            margin-bottom: 15px; 
            padding: 12px 16px; 
            border-radius: 12px;
            line-height: 1.5;
            animation: fadeIn 0.3s ease;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* User messages - right aligned, blue */
        .message.user { 
            background: linear-gradient(135deg, #0f3460 0%, #1a4a7a 100%);
            margin-left: 20%; 
            border-bottom-right-radius: 4px;
        }
        
        /* Assistant messages - left aligned, dark */
        .message.assistant { 
            background: rgba(26, 26, 46, 0.9);
            border: 1px solid #333; 
            margin-right: 20%;
            border-bottom-left-radius: 4px;
        }
        
        /* Role label */
        .role { 
            font-size: 0.7rem; 
            color: #888; 
            margin-bottom: 6px; 
            text-transform: uppercase;
            font-weight: 600;
            letter-spacing: 0.5px;
        }
        
        /* Message content */
        .content {
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        
        /* Input form */
        form { 
            display: flex; 
            gap: 10px; 
        }
        
        /* Text input */
        input[type="text"] { 
            flex: 1; 
            padding: 14px 18px; 
            border: 1px solid #333; 
            border-radius: 12px; 
            background: rgba(22, 33, 62, 0.9);
            color: #eee; 
            font-size: 16px;
            transition: border-color 0.2s, box-shadow 0.2s;
        }
        
        input[type="text"]:focus {
            outline: none;
            border-color: #00d9ff;
            box-shadow: 0 0 0 3px rgba(0, 217, 255, 0.1);
        }
        
        input[type="text"]::placeholder {
            color: #666;
        }
        
        /* Buttons */
        button { 
            padding: 14px 28px; 
            background: linear-gradient(135deg, #00d9ff 0%, #00b8d4 100%);
            color: #1a1a2e; 
            border: none; 
            border-radius: 12px; 
            cursor: pointer; 
            font-weight: 600;
            font-size: 15px;
            transition: transform 0.1s, box-shadow 0.2s;
        }
        
        button:hover { 
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0, 217, 255, 0.3);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        /* Clear button */
        .clear-btn { 
            background: linear-gradient(135deg, #e94560 0%, #c73e54 100%);
            color: white; 
        }
        
        .clear-btn:hover { 
            box-shadow: 0 4px 12px rgba(233, 69, 96, 0.3);
        }
        
        /* Empty state */
        .empty-state {
            text-align: center;
            color: #666;
            padding: 60px 20px;
        }
        
        .empty-state .icon {
            font-size: 3rem;
            margin-bottom: 15px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 {{ title }}</h1>
        
        <div class="chat-box" id="chat-box">
            {% if messages %}
                {% for msg in messages %}
                <div class="message {{ msg.role }}">
                    <div class="role">{{ msg.role }}</div>
                    <div class="content">{{ msg.content }}</div>
                </div>
                {% endfor %}
            {% else %}
                <div class="empty-state">
                    <div class="icon">💬</div>
                    <p>Start a conversation by typing a message below!</p>
                </div>
            {% endif %}
        </div>
        
        <form method="post" action="/chat">
            <input 
                type="text" 
                name="message" 
                placeholder="Type your message..." 
                autofocus 
                required
                autocomplete="off"
            >
            <button type="submit">Send</button>
            <button type="submit" formaction="/clear" class="clear-btn">Clear</button>
        </form>
    </div>
    
    <script>
        // Auto-scroll to bottom of chat
        const chatBox = document.getElementById('chat-box');
        chatBox.scrollTop = chatBox.scrollHeight;
    </script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# FastAPI Application
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler.
    
    This runs when the app starts and stops.
    We use it to clear conversation history on startup.
    """
    # Startup: clear any existing conversation
    conversation_history.clear()
    yield
    # Shutdown: nothing to clean up


# Create the FastAPI application instance
app = FastAPI(
    title=settings.app_name,
    description="A simple chat webapp using a local LLM",
    version="0.1.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Pydantic Models for API
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    """Request model for the chat API endpoint."""
    message: str


class ChatResponse(BaseModel):
    """Response model for the chat API endpoint."""
    response: str
    history: list[dict[str, str]]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    """Render the main chat interface.
    
    Returns the HTML page with the current conversation history.
    """
    template = Template(HTML_TEMPLATE)
    html = template.render(
        title=settings.app_name,
        messages=conversation_history
    )
    return HTMLResponse(content=html)


@app.post("/chat", response_class=HTMLResponse)
async def chat_web(message: str = Form(...)) -> HTMLResponse:
    """Handle chat form submission from the web interface.
    
    Args:
        message: The user's message from the form.
    
    Returns:
        The updated HTML page with the new messages.
    """
    # Add user message to history
    conversation_history.append({
        "role": "user",
        "content": message
    })
    
    try:
        # Get response from LLM
        response = chat_completion(conversation_history)
        
        # Add assistant response to history
        conversation_history.append({
            "role": "assistant",
            "content": response
        })
    except Exception as e:
        # If LLM fails, show error in chat
        conversation_history.append({
            "role": "assistant",
            "content": f"Sorry, I encountered an error: {e}"
        })
    
    # Re-render the page with updated history
    template = Template(HTML_TEMPLATE)
    html = template.render(
        title=settings.app_name,
        messages=conversation_history
    )
    return HTMLResponse(content=html)


@app.post("/clear", response_class=HTMLResponse)
async def clear_chat() -> HTMLResponse:
    """Clear the conversation history.
    
    Returns:
        The HTML page with empty conversation.
    """
    conversation_history.clear()
    
    template = Template(HTML_TEMPLATE)
    html = template.render(
        title=settings.app_name,
        messages=conversation_history
    )
    return HTMLResponse(content=html)


@app.post("/api/chat", response_model=ChatResponse)
async def chat_api(request: ChatRequest) -> ChatResponse:
    """API endpoint for programmatic chat access.
    
    This endpoint is useful for:
    - Testing the chat functionality
    - Building other clients that talk to this service
    - Integration with other systems
    
    Args:
        request: ChatRequest with the user's message.
    
    Returns:
        ChatResponse with the assistant's response and full history.
    """
    # Add user message
    conversation_history.append({
        "role": "user",
        "content": request.message
    })
    
    # Get LLM response
    response = chat_completion(conversation_history)
    
    # Add assistant response
    conversation_history.append({
        "role": "assistant",
        "content": response
    })
    
    return ChatResponse(
        response=response,
        history=conversation_history.copy()
    )


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint for Kubernetes liveness/readiness probes.
    
    Kubernetes will call this endpoint periodically to check if the
    application is running and ready to accept traffic.
    
    Returns:
        Simple status dictionary.
    """
    return {"status": "healthy"}


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

def main() -> None:
    """Entry point for running the application.
    
    This is called when you run `ai-chat` from the command line
    (defined in pyproject.toml [project.scripts]).
    """
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",  # Listen on all interfaces
        port=8000,
        log_level="info",
    )


# Allow running with `python -m ai_chat.app`
if __name__ == "__main__":
    main()