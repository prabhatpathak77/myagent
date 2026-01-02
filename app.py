from flask import Flask, render_template, request, jsonify, session, send_file
from flask_cors import CORS
from coordinator import CoordinatorAgent
import secrets
import threading
import speech_recognition as sr
from gtts import gTTS
import os
import tempfile
from datetime import datetime

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
CORS(app)

# Initialize coordinator (singleton)
coordinator = None
coordinator_lock = threading.Lock()

def get_coordinator():
    global coordinator
    if coordinator is None:
        with coordinator_lock:
            if coordinator is None:
                coordinator = CoordinatorAgent()
    return coordinator

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Get coordinator
        coord = get_coordinator()
        
        # Process user command
        response = coord.process_user_command(user_message)
        
        return jsonify({
            'success': True,
            'response': response
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/status', methods=['GET'])
def status():
    try:
        coord = get_coordinator()
        
        # Get quick status
        email_count = coord.email_agent.gmail.get_unread_emails(max_results=1)
        upcoming = coord.calendar_agent.calendar.get_upcoming_events(hours=24)
        
        return jsonify({
            'success': True,
            'status': {
                'unread_emails': len(email_count) if email_count else 0,
                'upcoming_events': len(upcoming) if upcoming else 0
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/voice/chat', methods=['POST'])
def voice_chat():
    temp_webm = None
    temp_wav = None
    
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        
        # Save the uploaded file
        timestamp = datetime.now().timestamp()
        temp_webm = os.path.join(tempfile.gettempdir(), f'audio_{timestamp}.webm')
        audio_file.save(temp_webm)
        
        # Check if file has content
        if os.path.getsize(temp_webm) == 0:
            return jsonify({
                'success': False,
                'error': 'Audio file is empty'
            }), 400
        
        # Convert WebM to WAV using pydub
        from pydub import AudioSegment
        
        # Try to load the audio file
        try:
            audio = AudioSegment.from_file(temp_webm)
        except Exception as e:
            # If webm fails, try as raw audio
            audio = AudioSegment.from_file(temp_webm, format="webm", codec="opus")
        
        temp_wav = os.path.join(tempfile.gettempdir(), f'audio_{timestamp}.wav')
        audio.export(temp_wav, format="wav", parameters=["-ar", "16000", "-ac", "1"])
        
        # Transcribe
        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_wav) as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
        
        # Process with Carlo
        coord = get_coordinator()
        response = coord.process_user_command(text)
        
        return jsonify({
            'success': True,
            'transcription': text,
            'response': response
        })
        
    except sr.UnknownValueError:
        return jsonify({
            'success': False,
            'error': 'Could not understand audio. Please speak clearly.'
        }), 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        # Clean up temp files
        if temp_webm and os.path.exists(temp_webm):
            try:
                os.remove(temp_webm)
            except:
                pass
        if temp_wav and os.path.exists(temp_wav):
            try:
                os.remove(temp_wav)
            except:
                pass

@app.route('/api/voice/synthesize', methods=['POST'])
def synthesize_speech():
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Generate speech
        tts = gTTS(text=text, lang='en', slow=False)
        temp_path = os.path.join(tempfile.gettempdir(), f'speech_{datetime.now().timestamp()}.mp3')
        tts.save(temp_path)
        
        return send_file(temp_path, mimetype='audio/mpeg')
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("Starting AI Personal Assistant Web Interface")
    print("=" * 60)
    print("\nInitializing coordinator agent...")
    get_coordinator()
    print("\n✓ Server ready!")
    print("✓ Open http://localhost:5001 in your browser")
    print("=" * 60 + "\n")
    app.run(debug=True, port=5001, use_reloader=False)
