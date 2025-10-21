from flask import Flask, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

def extract_audio_url(youtube_url, username=None, password=None):
    # 準備 ydl_opts，帶入帳號密碼（若有）
    ydl_opts = {}
    if username:
        ydl_opts["username"] = "paxyouta@gmail.com"
    if password:
        ydl_opts["password"] = "36ytilovetml"

    # 不下載，只抓資訊
    ydl_opts["quiet"] = True
    ydl_opts["nocheckcertificate"] = True

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        audio_url = None
        # 選最合適的音訊格式（優先acodec != none 且 vcodec == none）
        for f in info.get("formats", []):
            if f.get("acodec") and f.get("acodec") != "none" and (not f.get("vcodec") or f.get("vcodec") == "none"):
                audio_url = f.get("url")
                break
        # 如果找不到，嘗試取第一個有 url 的 format
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

    # 先從環境變數讀（RENDER_APP_USERNAME / RENDER_APP_PASSWORD），再覆蓋為 query 參數（若有）
    username = os.environ.get("YTDLP_USERNAME")
    password = os.environ.get("YTDLP_PASSWORD")

    # 若 user 在 GET 傳入 username/password，會用它（非常不安全）
    q_user = request.args.get("username")
    q_pass = request.args.get("password")
    if q_user:
        username = q_user
    if q_pass:
        password = q_pass

    if not username or not password:
        # 仍可嘗試無登入（公開影片）
        pass

    try:
        audio_url, info = extract_audio_url(youtube_url, username=username, password=password)
        if not audio_url:
            return jsonify({"error": "no audio url found", "info_keys": list(info.keys())}), 500
        return jsonify({"audio_url": audio_url, "title": info.get("title")})
    except Exception as e:
        # 把錯誤訊息回傳（方便偵錯）
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # 本機測試
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
