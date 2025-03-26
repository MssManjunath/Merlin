import os
import re
import ast

from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from .system_prompt import SYSTEM_PROMPT
from speech_modules.speech_recognition import listen_from_microphone
from speech_modules.speaking_module import speak

# Set your API key
os.environ["GOOGLE_API_KEY"] = "AIzaSyCp4MQZfPRZI7Cld15eiJX3ul9mvoIQJBA"


# Initialize LLM
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

os.environ["GOOGLE_API_KEY"] = "AIzaSyCp4MQZfPRZI7Cld15eiJX3ul9mvoIQJBA"
# GOOGLE_API_KEY=AIzaSyCp4MQZfPRZI7Cld15eiJX3ul9mvoIQJBA


import json

def extract_json_from_text(text: str):
    """
    Extracts a Python dict from text that may contain:
    - response = {...}
    - {...}
    - ```json\n{...}\n```
    """
    # Try to extract from "response = {...}"
    match = re.search(r"response\s*=\s*({.*})", text, re.DOTALL)
    if match:
        try:
            return ast.literal_eval(match.group(1))
        except Exception:
            pass

    # Try to extract from inside ```json ... ```
    match = re.search(r"```(?:json)?\s*({.*?})\s*```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass

    # Try to extract any lone {...}
    match = re.search(r"({.*})", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            try:
                return ast.literal_eval(match.group(1))
            except Exception:
                return None

    return None



def get_structured_response_with_context(user_input, state):
    # Build prompt differently based on whether we have an incomplete request
    if state.get("partial_json") and state.get("awaiting_info"):
        # Construct a context-aware prompt for completion
        context_prompt = f"""
                    You previously received this incomplete automation request:

                    response = {state['partial_json']}

                    The user has now provided additional input:
                    "{user_input}"

                    Use this to complete the missing fields (if possible), and return a full response in the same format as before."""
        prompt = f"{SYSTEM_PROMPT}\n\n{context_prompt.strip()}"
    else:
        # Regular new input prompt
        prompt = f"{SYSTEM_PROMPT}\n\nInput: \"{user_input}\"\n→"

    message = HumanMessage(content=prompt)
    response = llm.invoke([message])
    full_text = response.content.strip()

    # Split into acknowledgement + optional response
    lines = full_text.split("\n", 1)
    ack_message = lines[0]
    json_part = lines[1] if len(lines) > 1 else ""

    extracted_json = extract_json_from_text(json_part)

    print("\nBot says:", ack_message)
    if json_part:
        print("\nStructured response:\n" + json_part)

    return ack_message, extracted_json




# --- Main loop ---
def chat_start():
    conversation_state = {
        "partial_json": None,
        "awaiting_info": False
    }

    while True:
        # user_input = input("\nAsk something (or type 'exit'): ")
        # if user_input.lower() == "exit":
        #     break

        user_input = listen_from_microphone()
        if "exit" in user_input.lower():
          break

        ack, extracted_json = get_structured_response_with_context(user_input, conversation_state)


        speak(ack)
        if extracted_json:
            is_partial = extracted_json.get("partial", False)

            if is_partial:
                conversation_state["partial_json"] = extracted_json
                conversation_state["awaiting_info"] = True
                print("⏳ Waiting for more information to complete the command...")

            else:
                print("Triggering automation workflow with JSON:\n", extracted_json)

                conversation_state = {
                    "partial_json": None,
                    "awaiting_info": False
                }

        elif not extracted_json:
            print("General chat - no automation needed.")



