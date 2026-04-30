from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
from kb import load_kb, best_kb_match

load_dotenv()

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KB_PATH = os.path.join(BASE_DIR, "../data/data.json")
HISTORY_FILE = os.path.join(BASE_DIR, "../data/history.json")
USERS_FILE = os.path.join(BASE_DIR, "../data/users.json")

KB = load_kb(KB_PATH)

sessions = {}

# ===== MEMORY =====
def get_history(session_id):
    if session_id not in sessions:
        sessions[session_id] = [
            {"role": "system", "content": "Bạn là trợ lý AI thông minh"}
        ]
    return sessions[session_id]

# ===== USERS =====
def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def user_exists(username):
    return any(u.get("username") == username for u in load_users())

# ===== HISTORY =====
def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_history(session_id, username, user, bot, mode):
    data = load_history()

    data.append({
        "username": username,
        "session": session_id,
        "mode": mode,
        "user": user,
        "bot": bot,
        "time": datetime.now().strftime("%H:%M %d-%m-%Y")
    })

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ===== GROQ =====
def call_groq(messages):
    if not GROQ_API_KEY:
        return "Thiếu API KEY"

    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": GROQ_MODEL,
                "messages": messages
            },
            timeout=30
        )

        data = r.json()

        if not r.ok:
            print("GROQ ERROR:", data)
            return "Lỗi AI"

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        print("AI ERROR:", e)
        return "Lỗi server AI"

# ===== REGISTER =====
@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"msg": "Thiếu thông tin"})

        users = load_users()

        if any(u.get("username") == username for u in users):
            return jsonify({"msg": "Tài khoản đã tồn tại"})

        users.append({"username": username, "password": password})
        save_users(users)

        return jsonify({"msg": "Đăng ký thành công"})

    except Exception as e:
        print("REGISTER ERROR:", e)
        return jsonify({"msg": "Lỗi server"})

# ===== LOGIN =====
@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        users = load_users()

        for u in users:
            if u.get("username") == username and u.get("password") == password:
                return jsonify({"msg": "Đăng nhập thành công"})

        return jsonify({"msg": "Sai tài khoản hoặc mật khẩu"})

    except Exception as e:
        print("LOGIN ERROR:", e)
        return jsonify({"msg": "Lỗi server"})

# ===== CHAT =====
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(silent=True) or {}

        text = data.get("text", "").strip()
        username = data.get("username")
        session_id = data.get("session_id", "default")
        mode = data.get("mode", "ai")

        if not username or not user_exists(username):
            return jsonify({"reply": "Bạn cần đăng nhập"})

        if not text:
            return jsonify({"reply": "Bạn chưa nhập gì"})

        # ===== DATA MODE =====
        if mode == "data":
            kb_reply, _ = best_kb_match(text, KB)

            if kb_reply:
                save_history(session_id, username, text, kb_reply, mode)
                return jsonify({"reply": kb_reply})
            else:
                return jsonify({"reply": "Không có trong dữ liệu"})

        # ===== AI MODE =====
        if mode == "ai":
            history = get_history(session_id)

            history.append({"role": "user", "content": text})
            reply = call_groq(history)
            history.append({"role": "assistant", "content": reply})

            save_history(session_id, username, text, reply, mode)

            return jsonify({"reply": reply})

        return jsonify({"reply": "Mode không hợp lệ"})

    except Exception as e:
        print("CHAT ERROR:", e)
        return jsonify({"reply": "Lỗi server"})

# ===== HISTORY =====
@app.route("/history", methods=["GET"])
def history():
    try:
        username = request.args.get("username")

        data = load_history()

        #  FIX KEYERROR
        if username:
            data = [item for item in data if item.get("username") == username]

        return jsonify(data[-50:])  # luôn trả list

    except Exception as e:
        print(" HISTORY ERROR:", e)
        return jsonify([])

# ===== RUN =====
if __name__ == "__main__":
    print(" API running at http://127.0.0.1:5000")
    app.run(port=5000)