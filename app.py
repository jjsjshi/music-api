from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route("/get_audio_url", methods=["GET"])
def get_audio_url():
    youtube_url = request.args.get("url")
    if not youtube_url:
        return jsonify({"error": "no url provided"}), 400
    try:
        ydl_opts = {}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            audio_url = ''
            for f in info.get('formats', []):
                if f.get('acodec') != 'none' and f.get('vcodec') == 'none':
                    audio_url = f.get('url')
                    break
        return jsonify({"audio_url": audio_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
