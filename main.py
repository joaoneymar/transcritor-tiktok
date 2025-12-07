import os
import time
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import yt_dlp
import google.generativeai as genai

# Pega a chave dos Segredos do Replit
API_KEY = os.environ.get("GOOGLE_API_KEY")

app = Flask(__name__)
CORS(app)

genai.configure(api_key=API_KEY)

# --- ROTAS ---


# Rota Principal: AQUI ESTAVA O PROBLEMA!
# Agora ele manda mostrar o arquivo index.html em vez de texto puro
@app.route('/')
def home():
    return render_template('index.html')


# Rota do TikTok (O Motor)
@app.route('/transcrever', methods=['POST'])
def transcrever():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({"error": "URL não fornecida"}), 400

    temp_filename = f"audio_{int(time.time())}.mp3"

    # Configuração Camuflada para TikTok
    ydl_opts = {
        'format':
        'bestaudio/best',
        'outtmpl':
        temp_filename.replace('.mp3', ''),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet':
        True,
        'no_warnings':
        True,
        'nocheckcertificate':
        True,
        'user_agent':
        'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
    }

    try:
        # 1. Baixar
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)

        # 2. Upload para Gemini
        video_file = genai.upload_file(path=temp_filename)

        # Esperar processamento
        while video_file.state.name == "PROCESSING":
            time.sleep(1)
            video_file = genai.get_file(video_file.name)

        # 3. Transcrever com modelo 2.5
        model = genai.GenerativeModel(model_name="gemini-2.5-flash")
        prompt = "Transcreva este áudio palavra por palavra. Mantenha em português."
        response = model.generate_content([video_file, prompt])

        # 4. Limpar
        try:
            genai.delete_file(video_file.name)
            if os.path.exists(temp_filename): os.remove(temp_filename)
        except:
            pass

        return jsonify({"transcription": response.text})

    except Exception as e:
        if os.path.exists(temp_filename): os.remove(temp_filename)
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
