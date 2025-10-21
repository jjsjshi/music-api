from flask import Flask, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

def extract_audio_url(youtube_url):
    # yt-dlp 選項
    ydl_opts = {
        "format": "bestaudio",
        "quiet": True,
        "nocheckcertificate": True,
        "http_headers": {
            # 模擬真實瀏覽器 User-Agent
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
        }
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        audio_url = None
        # 選最合適音訊
        for f in info.get("formats", []):
            if f.get("acodec") and f.get("acodec") != "none" and (not f.get("vcodec") or f.get("vcodec") == "none"):
                audio_url = f.get("url")
                break
        # 如果找不到，取第一個有 url 的 format
        if not audio_url:
            for f in info.get("formats", []):
                if f.get("url"):
                    audio_url = f.get("url")
                    break
        return audio_url, info

@app.route("/get_audio_url", methods=["GET"])
def get_audio_url():
    youtube_url = request.args.get("url")
    if not youtube_url:
        return jsonify({"error": "no url provided"}), 400

    try:
        audio_url, info = extract_audio_url(youtube_url)
        if not audio_url:
            return jsonify({"error": "no audio url found", "info_keys": list(info.keys())}), 500
        return jsonify({"audio_url": audio_url, "title": info.get("title")})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
