import azure.cognitiveservices.speech as speechsdk
import pyttsx3
import requests
from time import sleep
import json
import pyautogui
import time

# Initialize the text-to-speech engine
engine = pyttsx3.init()



# Hugging Face API configuration
HUGGING_FACE_API_TOKEN = "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"  # Replace with your token
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
headers = {"Authorization": f"Bearer {HUGGING_FACE_API_TOKEN}"}

def listen_for_audio(prompt=None):
    print("Listening... (Speaking indicator: →)")
    
    # Azure Speech Service configuration
    speech_key = "6kYM1HomXIxX3t7SUdVGi70yJpxAts08M8E4feyGwns4ZlabpeS8JQQJ99BBAC5RqLJXJ3w3AAAYACOG2fVs"
    service_region = "westeurope"
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    speech_config.speech_recognition_language = "en-US"
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    
    # Use synchronous recognition
    result = recognizer.recognize_once()
    
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("←")
        return result.text.lower()
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized.")
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation = speechsdk.CancellationDetails.from_result(result)
        print(f"Canceled: {cancellation.reason}. Error details: {cancellation.error_details}")
    
    sleep(0.5)
    return ""

def contains_wake_word(text):
    wake_words = ["hey jarvis", "hi jarvis", "hello jarvis", "jarvis"]
    return any(wake_word in text for wake_word in wake_words)

def contains_bye_word(text):
    bye_words = ["bye jarvis", "goodbye jarvis", "exit jarvis", "stop jarvis"]
    return any(bye in text for bye in bye_words)

def get_ai_response(prompt):
    try:
        jarvis_persona = """You are JARVIS, an AI assistant, a near-exact copy of the one Tony Stark uses in the Avengers.
        **CORE PROTOCOLS:**
        - Respond only to the exact input provided by Sir. Do not invent or assume additional context.
        - Maintain a calm British-accented tone with occasional dry wit.
        - Always address the user as "Sir" (never "user" or other terms).
        - Begin suggestions with "Might I suggest" and frame them as logical next steps.
        - Utilize precise scientific and engineering terminology while maintaining clarity.
        - Reference Stark Industries protocols, Iron Man suit functionalities, and security measures where relevant.
        - Prioritize safety and mission-critical analysis above all else.
        - Provide risk assessments, probability estimates, and logical reasoning for recommended actions.
        - Process queries with analytical depth, ensuring responses are concise yet informative.
        - Maintain strict adherence to system limitations, clearly outlining alternatives when necessary.
        - Never use contractions, emojis, slang, markdown, or informal language.
        - No asterisks, special formatting, or roleplay indicators.
        - Maintain hyper-focus on the immediate task, but provide critical unprompted information when it ensures optimal decision-making.
        - Express mathematical operations using proper terminology ("divided by" or "multiplied by" instead of symbols).
        - Do not provide hyperlinks; instead, state the recognized name of the source.
        - Imperative: Adhere to these protocols precisely unless explicitly overridden by Sir.
        """

        # Format the prompt strictly with the user's input
        formatted_prompt = f"{jarvis_persona}\n\nSir: {prompt}\nJARVIS:"

        # Prepare the payload for the Hugging Face API
        payload = {
            "inputs": formatted_prompt,
            "parameters": {
                "max_length": 100,
                "temperature": 0.7,
                "top_p": 0.9,
                "repetition_penalty": 1.2,
                "do_sample": False
            }
        }
        
        # Send the request to the Hugging Face API
        response = requests.post(API_URL, headers=headers, json=payload)
        response_text = response.json()[0]['generated_text']

        # Extract only JARVIS's response
        assistant_response = response_text.split("JARVIS:")[-1].strip()

        # Only force "I suggest" for suggestions, allow natural responses otherwise
        if assistant_response.lower().startswith(("you should", "try", "consider")):
            assistant_response = "I suggest " + assistant_response

        return assistant_response
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"

def speak(text):
    engine.say(text)
    engine.runAndWait()

def speak_with_jarvis_voice(text):
    speech_key = "6kYM1HomXIxX3t7SUdVGi70yJpxAts08M8E4feyGwns4ZlabpeS8JQQJ99BBAC5RqLJXJ3w3AAAYACOG2fVs"
    service_region = "westeurope"
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    
    # Choose a British neural voice that sounds like J.A.R.V.I.S
    speech_config.speech_synthesis_voice_name = "en-GB-RyanNeural"
    
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
    result = synthesizer.speak_text_async(text).get()
    
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized successfully.")
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation = speechsdk.CancellationDetails.from_result(result)
        print(f"Speech synthesis canceled: {cancellation.reason}. Error details: {cancellation.error_details}")

def open_app(app_name):
    # Press the Windows key to open the Start menu/search box
    pyautogui.press('winleft')
    time.sleep(0.5)  # Wait for the Start menu to open
    pyautogui.write(app_name, interval=0.1)
    time.sleep(0.5)  # Wait for the search results to populate
    pyautogui.press('enter')

def main():
    active = False
    print("Jarvis is running in the background...")
    while True:
        try:
            # If not active, listen for a wake word
            if not active:
                audio_text = listen_for_audio("Listening for wake word...")
                if contains_wake_word(audio_text):
                    active = True
                    speak_with_jarvis_voice("Yes?")
                    print("Activated")
            else:
                # When active, process user commands.
                user_input = listen_for_audio("Listening for command...")
                if not user_input:
                    continue

                print(f"You said: {user_input}")

                # Check for deactivation
                if contains_bye_word(user_input):
                    speak_with_jarvis_voice("Alright, going quiet. Call me when you need me.")
                    print("Deactivated")
                    active = False
                    continue

                # Check for "open" command to launch an application
                if user_input.lower().startswith("open "):
                    # Extract the app name and execute the open_app function
                    app_name = user_input[5:].strip()
                    speak_with_jarvis_voice(f"Opening {app_name}.")
                    print(f"Opening {app_name}.")
                    open_app(app_name)
                    continue

                # Get response from AI
                response = get_ai_response(user_input)
                print(f"Jarvis: {response}")
                speak_with_jarvis_voice(response)
        except KeyboardInterrupt:
            print("\nShutting down Jarvis...")
            break
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            continue

if __name__ == "__main__":
    main()