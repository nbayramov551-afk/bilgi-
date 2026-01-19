from flask import Flask, render_template, request, jsonify
from deep_translator import GoogleTranslator
import speech_recognition as sr
import os, uuid, asyncio, edge_tts

app = Flask(__name__)

# Neural Səslər Databazası
VOICE_DB = {
    'en': 'en-US-ChristopherNeural', 'tr': 'tr-TR-AhmetNeural', 'ru': 'ru-RU-DmitryNeural',
    'de': 'de-DE-ConradNeural', 'fr': 'fr-FR-HenriNeural', 'ar': 'ar-SA-HamedNeural',
    'it': 'it-IT-DiegoNeural', 'ja': 'ja-JP-KeitaNeural', 'ko': 'ko-KR-InJoonNeural',
    'es': 'es-ES-AlvaroNeural'
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_voice', methods=['POST'])
def process_voice():
    try:
        lang_code = request.form.get('lang', 'en')
        audio_file = request.files['audio_data']
        uid = str(uuid.uuid4())
        raw_p, clean_p = f"raw_{uid}.webm", f"clean_{uid}.wav"
        audio_file.save(raw_p)

        # Səs təmizləmə (FFmpeg mütləqdir)
        os.system(f"ffmpeg -i {raw_p} -af 'highpass=f=80, lowpass=f=8000, afftdn' -ar 16000 -ac 1 -y {clean_p}")

        rec = sr.Recognizer()
        with sr.AudioFile(clean_p) as source:
            audio_data = rec.record(source)
            text = rec.recognize_google(audio_data, language='az-AZ')
            translated = GoogleTranslator(source='az', target=lang_code).translate(text)

            if not os.path.exists('static'): os.makedirs('static')
            out_mp3 = f"static/ismail_{uid}.mp3"
            
            async def generate():
                v = VOICE_DB.get(lang_code, 'en-US-ChristopherNeural')
                await edge_tts.Communicate(translated, v).save(out_mp3)
            
            asyncio.run(generate())
            
            os.remove(raw_p); os.remove(clean_p)
            return jsonify({"original": text, "translated": translated, "audio_url": "/" + out_mp3})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
  
