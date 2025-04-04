import os
import re
import ast
import json


from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from .system_prompt import SYSTEM_PROMPT,SYSTEM_PROMPT_V_1,SYSTEM_PROMPT_WITH_MEMORY, SYSTEM_PROMPT_WITH_MEMORY_V1
from speech_modules.speech_recognition import listen_from_microphone
from speech_modules.speaking_module import speak
from memory.memory_updater.memory_updater import update_memory,load_file
import datetime

# Set your API key

# Initialize LLM
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

CURRENT_PROMPT = SYSTEM_PROMPT_WITH_MEMORY_V1


def extract_combined_response(text):
    match = re.search(r"response\s*=\s*({.*})", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except:
            try:
                return ast.literal_eval(match.group(1))
            except:
                pass
    
    match = re.search(r"```(?:json)?\s*({.*?})\s*```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass
    
    return None



def get_structured_response_with_context(user_input, state,timestamp):

    previous_memory = load_file()
    memory_context = f"\n\nHere is the saved memory context you may use:\n{json.dumps(previous_memory, indent=2)}"

    if state.get("partial_json") and state.get("awaiting_info"):
        # Construct a context-aware prompt for completion
        context_prompt = f"""
                    You previously received this incomplete automation request:

                    response = {state['partial_json']}

                    The user has now provided additional input:
                    "{user_input}"

                    and was asked at:
                    "{timestamp}"

                    Use this to complete the missing fields (if possible), and return a full response in the same format as before."""
        prompt = f"{CURRENT_PROMPT}{memory_context}\n\n{context_prompt.strip()}"
    else:
        # Regular new input prompt
        prompt = f"{CURRENT_PROMPT}{memory_context}\n\nInput: \"{user_input}\"\nAsked at: {timestamp}\n→"

    message = HumanMessage(content=prompt)
    response = llm.invoke([message])
    full_text = response.content.strip()

    parsed = extract_combined_response(full_text)
    if parsed is None:
        print("⚠️ No structured response parsed.")
        return full_text.split("\n")[0], None, None

    ack_message = full_text.split("\n")[0]
    actionable = parsed.get("actionable")
    memory_update = parsed.get("memory_update")


    return ack_message, actionable, memory_update



def wake_up_bot(conversation_state):
    
    speak("Lets go Boss")
    while True:
        # user_input = listen_from_microphone()
        user_input = input("Type something: ")

        timestamp = datetime.datetime.now().isoformat()
        if "exit" in user_input.lower():
          break

        ack, actionable, memory_update = get_structured_response_with_context(user_input, conversation_state,timestamp)

        speak(ack)
        print(ack)
        if memory_update:
            print("Writing to memory")
            update_memory(memory_update)


        if actionable:
            is_partial = actionable.get("partial", False)

            if is_partial:
                conversation_state["partial_json"] = actionable
                conversation_state["awaiting_info"] = True
                print("Waiting for more information to complete the command...")

            else:
                print("Triggering automation workflow with JSON:\n", actionable)

                conversation_state = {
                        "partial_json": None,
                        "awaiting_info": False
                }

        elif not actionable:
            print("General chat - no automation needed.")


def chat_start():
    conversation_state = {
        "partial_json": None,
        "awaiting_info": False
    }

    while True:
        # user_input = listen_passive()
        user_input = input("Type something (wake word): ")
        if "merlin" in user_input.lower():
            wake_up_bot(conversation_state)







