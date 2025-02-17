import os
import re
import difflib
import json
import requests
from openai import OpenAI
from dotenv import load_dotenv
import whisper_timestamped as whisper
from config.config import CONFIG

load_dotenv()

class ScriptController:
    def __init__(self):
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
        self.client = OpenAI(api_key=self.OPENAI_API_KEY)
    
    def generate_script(self, system_content, user_content, model, script_path):
        try:
            completion = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": user_content}
                ]
            )
            script = completion.choices[0].message.content
            with open(script_path, 'w') as script_file:
                script_file.write(script)
            return self.clean_script(script)
        except Exception as e:
            print(f"Error generating script: {e}")
            return None

    def generate_audio(self, text, provider, audio_path):
        provider = provider.lower()
        if provider == "openai":

            openai_config = CONFIG.get("audio_settings", {}).get("openai", {})
            model = openai_config.get("model", "tts-1-hd")
            voice = openai_config.get("voice", "onyx")
            response = self.client.audio.speech.create(
                model=model,
                voice=voice,
                input=text,
            )
            response.stream_to_file(audio_path)

        elif provider == "elevenlabs":

            elevenlabs_config = CONFIG.get("audio_settings", {}).get("elevenlabs", {})
            model_id = elevenlabs_config.get("model_id", "pNInz6obpgDQGcFmaJgB")
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{model_id}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.ELEVENLABS_API_KEY
            }
            data = {
                "text": text,
                "model": elevenlabs_config.get("model", "eleven_monolingual_v1"),
                "voice_settings": elevenlabs_config.get("voice_settings", {"stability": 0.5, "similarity_boost": 0.5})
            }
            response = requests.post(url, json=data, headers=headers)
            CHUNK_SIZE = 1024
            with open(audio_path, 'wb') as audio_file:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:
                        audio_file.write(chunk)
        else:
            raise ValueError(f"Unknown audio provider: {provider}")

    def generate_transcript(self, audio_file, transcript_file_path):
        audio = whisper.load_audio(audio_file)
        whisper_model = CONFIG.get("whisper_settings", {}).get("model", "base")
        device = CONFIG.get("whisper_settings", {}).get("device", "cpu")
        model = whisper.load_model(whisper_model, device=device)
        result = whisper.transcribe(model, audio, language="en")
        transcript_str = json.dumps(result, indent=2, ensure_ascii=False)
        with open(transcript_file_path, 'w') as transcript_file:
            transcript_file.write(transcript_str)
        print(f"Transcript:\n{transcript_str}")
        return result

    def verify_transcript(self, transcript_file, project_path, threshold=0.7):
        script_path = os.path.join(project_path, "script.txt")
        try:
            with open(script_path, 'r') as f:
                original_script = f.read().strip()
        except Exception as e:
            print("Script file not found for verification.")
            return None

        try:
            with open(transcript_file, 'r') as f:
                transcript_data = json.load(f)
        except Exception as e:
            print("Could not load transcript file for verification:", e)
            return None

        full_transcript = " ".join(
            word.get("text", "") for segment in transcript_data.get("segments", []) for word in segment.get("words", [])
        ).strip()
        
        similarity = difflib.SequenceMatcher(None, original_script, full_transcript).ratio()
        print(f"Transcript similarity to original script: {similarity:.2f}")
        if similarity < threshold:
            print(f"Warning: Transcript similarity is below the threshold of {threshold}.")
        else:
            print("Transcript verification passed.")
        return similarity

    def clean_script(self, script):
        script = script.replace("'", '"')
        script = script.replace("*", "")
        script = re.sub(r'\([^)]*\)', '', script)
        return script 