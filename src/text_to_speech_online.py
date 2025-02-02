import tempfile
from gtts import gTTS
import subprocess
import time
from mutagen.mp3 import MP3  # New import for duration detection
from langdetect import detect as langdetect_detect
import re
import fasttext
import io
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource """
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Load model with correct path
LID_MODEL = fasttext.load_model(resource_path('models/lid.176.bin'))

def clean_text_for_detection(text):
    """Clean text for better language detection"""
    # Remove URLs, emails, special chars
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'\S+@\S+', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip()

def detect_language(text):
    """Combined language detection using fasttext and langdetect"""
    try:
        # First try fasttext
        predictions = LID_MODEL.predict(text.replace("\n", " "))
        lang_code = predictions[0][0].replace('__label__', '')
        confidence = predictions[1][0]
        
        if confidence > 0.7:
            return lang_code
    except Exception as e:
        pass
    
    # Fallback to langdetect
    try:
        return langdetect_detect(text)
    except:
        return 'en'  # Final fallback

def normalize_lang_code(code):
    """Normalize language codes for TTS compatibility"""
    LANGUAGE_MAP = {
        'zh': 'zh-cn', 'jp': 'ja', 'kr': 'ko',
        'iw': 'he', 'in': 'id', 'tl': 'fil'
    }
    code = code.split('-')[0].lower()
    return LANGUAGE_MAP.get(code, code)

def speak(text, lang=None, volume=80):
    # Enhanced empty check with proper character stripping
    if not text.strip('\'"""''?!-–— \t\n\r'):
        return
    
    try:
        # Auto-detect language if not specified
        if lang is None:
            cleaned = clean_text_for_detection(text)
            detected = detect_language(cleaned)
            lang = normalize_lang_code(detected)

            # fixed for wxc only
            if lang not in ['en', 'zh-cn']:
                lang = 'zh-cn'

        # for windows
        if os.name == 'nt':
            try:
                import win32com.client
                speaker = win32com.client.Dispatch("SAPI.SpVoice")
                
                # Set voice based on language
                voices = speaker.GetVoices()
                if lang == 'zh-cn':
                    # Find Chinese voice
                    for voice in voices:
                        if 'Chinese' in voice.GetDescription():
                            speaker.Voice = voice
                            break
                else:
                    # Default to English voice
                    for voice in voices:
                        if 'English' in voice.GetDescription():
                            speaker.Voice = voice
                            break
                
                # Set volume (0-100)
                speaker.Volume = volume
                speaker.Speak(text)
                
            except ImportError:
                # Fallback to using powershell if pywin32 is not installed
                if lang == 'zh-cn':
                    # Use Chinese voice in PowerShell
                    subprocess.run(['powershell', '-Command', 
                        f'Add-Type -AssemblyName System.speech; $speaker = New-Object System.speech.synthesis.speechSynthesizer; $speaker.SelectVoice("Microsoft Huihui Desktop"); $speaker.Speak("{text}")'], 
                        check=True)
                else:
                    # Use default English voice
                    subprocess.run(['powershell', '-Command', 
                        f'Add-Type -AssemblyName System.speech; (New-Object System.speech.synthesis.speechSynthesizer).Speak("{text}")'], 
                        check=True)
        else:
            # Non-Windows systems use gTTS
            tts = gTTS(text=text, lang=lang)
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=True) as temp_file:
                tts.write_to_fp(temp_file)
                temp_file.flush()
                volume_level = max(0.0, min(1.0, volume / 100))
                player = subprocess.Popen(['afplay', '-v', str(volume_level), temp_file.name])
                time.sleep(len(text.split()) * 0.3)
        
    except AssertionError:
        print(f"Skipped problematic text: '{text}'")
    except Exception as e:
        print(f"Speech error: {str(e)}")


if __name__ == "__main__":
    input_text = input("Enter text to speak: ")
    speak(input_text) 