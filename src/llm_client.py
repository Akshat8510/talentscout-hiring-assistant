import os
import json
import re
from groq import Groq
from src.prompts import build_system_prompt

def chat(messages, collected_data, phase):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError("Set GROQ_API_KEY in your .env file.")
    
    client = Groq(api_key=api_key)
    system_instruction = build_system_prompt(collected_data, phase)
    
    groq_messages = []
    for i, m in enumerate(messages):
        content = m["content"]
        if i == len(messages) - 1 and m["role"] == "user":
            content = (
                "SYSTEM RULES:\n" + system_instruction + "\n\n"
                "USER MESSAGE: " + content + "\n\n"
                "CRITICAL FORMAT RULES:\n"
                "- Your response MUST have exactly two sections separated by the marker.\n"
                "- Section 1: Your conversational reply ONLY. No JSON here.\n"
                "- Section 2: Extracted JSON ONLY. No text here.\n"
                "- Use this EXACT format with no deviation:\n\n"
                "REPLY:\n"
                "<your reply here, no JSON>\n"
                "EXTRACTED_JSON:\n"
                "{\"Field\": \"value\"}\n\n"
                "Fields to extract from USER MESSAGE only: "
                "Full Name, Email Address, Phone Number, Current Location, "
                "Years of Experience, Desired Position(s), Tech Stack.\n"
                "If no new fields found, output: {}"
            )
        groq_messages.append({"role": m["role"], "content": content})

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=groq_messages,
            max_tokens=1024,
            temperature=0.7,
        )
        raw = response.choices[0].message.content
        return _parse(raw)
    except Exception as e:
        return f"⚠️ Error: {str(e)[:120]}", {}


def _parse(raw):
    reply, extracted = raw.strip(), {}
    try:
        if "EXTRACTED_JSON:" in raw:
            # Split on the marker
            parts = raw.split("EXTRACTED_JSON:", 1)
            # Clean the reply part
            reply = parts[0].replace("REPLY:", "").strip()
            # Clean the JSON part
            json_part = parts[1].strip()
            json_part = re.sub(r"```json|```", "", json_part).strip()
            # Extract only the first valid JSON object
            json_match = re.search(r"\{.*?\}", json_part, re.DOTALL)
            if json_match:
                extracted = json.loads(json_match.group())
        else:
            # Fallback: strip any stray JSON from reply
            json_match = re.search(r"\{[^{}]+\}", raw, re.DOTALL)
            if json_match:
                extracted = json.loads(json_match.group())
                reply = raw[:json_match.start()].strip()
    except Exception:
        pass

    # Final cleanup — remove any leaked markers from reply
    reply = reply.replace("REPLY:", "").replace("EXTRACTED_JSON:", "").strip()
    # Remove any trailing { that might have leaked
    reply = re.sub(r"\{.*", "", reply, flags=re.DOTALL).strip()

    return reply, extracted


def extract_info(user_input, current_data):
    return {}