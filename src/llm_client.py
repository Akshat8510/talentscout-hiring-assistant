"""
llm_client.py — Thin wrapper around the Anthropic Claude API.
"""
import os
import google.generativeai as genai
from src.prompts import build_system_prompt

def get_model():
    """Initialize and return the Gemini model."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY is not set. Please check your .env file.")
    
    genai.configure(api_key=api_key)
    
    # We use gemini-1.5-flash: it's fast, smart, and free.
    return genai.GenerativeModel(
        model_name="gemini-1.5-flash",
    )

def chat(
    messages: list[dict],
    collected_data: dict,
    phase: str,
) -> str:
    """
    Send the conversation history to Gemini and return the response.
    """
    model = get_model()
    system_instruction = build_system_prompt(collected_data, phase)
    
    # Gemini 1.5 supports system_instructions directly in the model config
    # but for a simple chat history, we can prepend it or use the start_chat method.
    
    # Convert Streamlit/Claude format to Gemini format
    # Roles: 'user' stays 'user', 'assistant' becomes 'model'
    history = []
    for m in messages[:-1]: # All messages except the last one
        role = "user" if m["role"] == "user" else "model"
        history.append({"role": role, "parts": [m["content"]]})
    
    # The last message is the current user input
    user_input = messages[-1]["content"]

    # Start chat with system instruction
    # Note: We re-initialize the model with the system instruction to keep it context-aware
    chat_model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=system_instruction
    )
    
    chat_session = chat_model.start_chat(history=history)
    response = chat_session.send_message(user_input)
    
    return response.text