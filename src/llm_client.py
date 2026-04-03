import os
import google.generativeai as genai
from src.prompts import build_system_prompt

def chat(
    messages: list[dict],
    collected_data: dict,
    phase: str,
) -> str:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return "⚠️ Error: GOOGLE_API_KEY not found."
    
    # Configure the API
    genai.configure(api_key=api_key)
    
    # SYSTEM PROMPT
    system_instruction = build_system_prompt(collected_data, phase)

    # 🚨 FIX: Using the EXACT model name found in your terminal logs
    # Your terminal showed 'models/gemini-2.0-flash' is available!
    model_name = "gemini-2.0-flash" 

    model = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=system_instruction
    )
    
    # ── FORMAT HISTORY ──────────────────────────────────────────────────────
    gemini_history = []
    for m in messages[:-1]:
        role = "user" if m["role"] == "user" else "model"
        gemini_history.append({"role": role, "parts": [m["content"]]})
    
    # Ensure history starts with 'user' role
    if gemini_history and gemini_history[0]["role"] == "model":
        gemini_history.insert(0, {"role": "user", "parts": ["Hi, let's start."]})

    user_input = messages[-1]["content"]

    try:
        chat_session = model.start_chat(history=gemini_history)
        response = chat_session.send_message(user_input)
        return response.text
    except Exception as e:
        print(f"❌ ERROR WITH {model_name}: {e}")
        
        # SECOND CHANCE: Try 'gemini-flash-latest' which was also in your 'Found' list
        try:
            print("🔄 Trying fallback to gemini-flash-latest...")
            fallback = genai.GenerativeModel("gemini-flash-latest", system_instruction=system_instruction)
            res = fallback.generate_content(user_input)
            return res.text
        except:
            return f"Final Connection Error. Please check terminal logs."