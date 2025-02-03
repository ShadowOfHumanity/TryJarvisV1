import speech_recognition as sr
from vosk import Model, KaldiRecognizer
import pyaudio
import json
import pyttsx3
import requests
from time import sleep

# Initialize Vosk model
model = Model(lang="en-us")
recognizer = KaldiRecognizer(model, 16000)

# Audio stream setup
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
stream.start_stream()

# Initialize the text-to-speech engine
engine = pyttsx3.init()

# Hugging Face API configuration
HUGGING_FACE_API_TOKEN = "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"  # Replace with your token
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"#"https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"
headers = {"Authorization": f"Bearer {HUGGING_FACE_API_TOKEN}"}

def listen_for_audio(prompt=None):
    if prompt:
        print(prompt)
    print("Listening... (Speaking indicator: →)")
    
    data = b""
    while True:
        chunk = stream.read(4000, exception_on_overflow=False)
        if len(chunk) == 0:
            break
        
        if recognizer.AcceptWaveform(chunk):
            result = json.loads(recognizer.Result())
            if result.get("text", ""):
                print("←")  # Indicate end of listening
                return result["text"].lower()
        
        # Visual feedback
        print("→", end="\r")
        
    return ""

def contains_wake_word(text):
    wake_words = ["hey jarvis", "hi jarvis", "hello jarvis", "jarvis"]
    return any(wake_word in text for wake_word in wake_words)

def contains_bye_word(text):
    bye_words = ["bye jarvis", "goodbye jarvis", "exit jarvis", "stop jarvis"]
    return any(bye in text for bye in bye_words)

def get_ai_response(prompt):
    try:
        formatted_prompt = f"""<s>[INST] You are JARVIS, an AI assistant, A ALMOST COPY of the one that Tony Stark Has in the Avengers
        RULES:
        - Give detailed, thoughtful responses
        - Start suggestions with "I suggest"
        - Use natural conversation style
        - Stay focused on the topic
        - Be helpful and informative
        - Refer to me as Sir
        - No asteriks or special characters
        
        
        Human: {prompt}
        Assistant: [/INST]"""
        
        payload = {
            "inputs": formatted_prompt,
            "parameters": {
                "max_length": 500,  # Increased length
                "temperature": 0.8,  # More creative
                "top_p": 0.95,
                "repetition_penalty": 1.15
            }
        }
        response = requests.post(API_URL, headers=headers, json=payload)
        response_text = response.json()[0]['generated_text']
        assistant_response = response_text.split("[/INST]")[-1].strip()
        
        # Only force "I suggest" for suggestions, allow natural responses otherwise
        if assistant_response.lower().startswith(("you should", "try", "consider")):
            assistant_response = "I suggest " + assistant_response
            
        return assistant_response
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"

def speak(text):
    engine.say(text)
    engine.runAndWait()

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
                    speak("Yes?")
                    print("Activated")
            else:
                # When active, process user commands.
                user_input = listen_for_audio("Listening for command...")
                if not user_input:
                    continue

                print(f"You said: {user_input}")

                # Check for deactivation
                if contains_bye_word(user_input):
                    speak("Alright, going quiet. Call me when you need me.")
                    print("Deactivated")
                    active = False
                    continue

                # Get response from AI
                response = get_ai_response(user_input)
                print(f"Jarvis: {response}")
                speak(response)
        except KeyboardInterrupt:
            print("\nShutting down Jarvis...")
            break
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            continue

if __name__ == "__main__":
    main()