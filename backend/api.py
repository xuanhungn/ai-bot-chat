from flask import Flask, request, jsonify, g, send_from_directory, abort
from flask_cors import CORS
import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
from kb import load_kb, best_kb_match
from auth import (
    hash_password,
    verify_password,
    create_token,
    require_auth,
)

load_dotenv()

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KB_PATH = os.path.join(BASE_DIR, "../data/data.json")
HISTORY_FILE = os.path.join(BASE_DIR, "../data/history.json")
USERS_FILE = os.path.join(BASE_DIR, "../data/users.json")
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "../frontend"))

KB = load_kb(KB_PATH)
sessions = {}


def get_history(session_id):
    if session_id not in sessions:
        sessions[session_id] = [
            {"role": "system", "content": "Bạn là trợ lý AI thông minh, trả lời bằng tiếng Việt."}
        ]
    return sessions[session_id]


def load_json_file(path):
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error loading {path}: {e}")
        return []


def save_json_file(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_users():
    return load_json_file(USERS_FILE)


def save_users(users):
    save_json_file(USERS_FILE, users)


def user_exists(username):
    return any(u.get("username") == username for u in load_users())


def find_user(username):
    for u in load_users():
        if u.get("username") == username:
            return u
    return None


def upgrade_password(username, password):
    users = load_users()
    for u in users:
        if u.get("username") == username:
            u["password"] = hash_password(password)
            break
    save_users(users)


def load_history():
    return load_json_file(HISTORY_FILE)


def save_history(session_id, username, user, bot, mode):
    data = load_history()
    data.append({
        "username": username,
        "session": session_id,
        "mode": mode,
        "user": user,
        "bot": bot,
        "time": datetime.now().strftime("%H:%M %d-%m-%Y"),
    })
    save_json_file(HISTORY_FILE, data)


def call_groq(messages):
    if not GROQ_API_KEY:
        return "Thiếu API KEY"

    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={"model": GROQ_MODEL, "messages": messages},
            timeout=30,
        )
        data = r.json()

        if not r.ok:
            print("GROQ ERROR:", data)
            return "Lỗi AI"

        return data["choices"][0]["message"]["content"]

    except (requests.RequestException, KeyError, IndexError) as e:
        print("AI ERROR:", e)
        return "Lỗi server AI"


@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json() or {}
        username = data.get("username", "").strip()
        password = data.get("password", "")

        if not username or not password:
            return jsonify({"msg": "Thiếu thông tin"})

        if len(password) < 4:
            return jsonify({"msg": "Mật khẩu tối thiểu 4 ký tự"})

        if user_exists(username):
            return jsonify({"msg": "Tài khoản đã tồn tại"})

        users = load_users()
        users.append({"username": username, "password": hash_password(password)})
        save_users(users)

        return jsonify({"msg": "Đăng ký thành công"})

    except Exception as e:
        print("REGISTER ERROR:", e)
        return jsonify({"msg": "Lỗi server"})


@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json() or {}
        username = data.get("username", "").strip()
        password = data.get("password", "")

        user = find_user(username)
        if not user or not verify_password(user.get("password", ""), password):
            return jsonify({"msg": "Sai tài khoản hoặc mật khẩu"})

        stored = user.get("password", "")
        if not stored.startswith("$2b$") and not stored.startswith("$2a$"):
            upgrade_password(username, password)

        token = create_token(username)
        return jsonify({"msg": "Đăng nhập thành công", "token": token, "username": username})

    except Exception as e:
        print("LOGIN ERROR:", e)
        return jsonify({"msg": "Lỗi server"})


@app.route("/chat", methods=["POST"])
@require_auth
def chat():
    try:
        data = request.get_json(silent=True) or {}

        text = data.get("text", "").strip()
        username = g.username
        session_id = data.get("session_id", "default")
        mode = data.get("mode", "ai")

        if not text:
            return jsonify({"reply": "Bạn chưa nhập gì"})

        if mode == "data":
            kb_reply, _ = best_kb_match(text, KB)
            reply = kb_reply or "Không có trong dữ liệu"
            save_history(session_id, username, text, reply, mode)
            return jsonify({"reply": reply})

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


@app.route("/history", methods=["GET"])
@require_auth
def history():
    try:
        username = g.username
        data = load_history()
        data = [item for item in data if item.get("username") == username]
        return jsonify(data[-50:])

    except Exception as e:
        print("HISTORY ERROR:", e)
        return jsonify([])


# ==========================
# FRONTEND
# ==========================

# Trang mặc định là Login
@app.route("/", methods=["GET"])
def serve_root():
    return send_from_directory(FRONTEND_DIR, "login.html")


# Trang Login
@app.route("/login.html", methods=["GET"])
def serve_login():
    return send_from_directory(FRONTEND_DIR, "login.html")


# Trang Đăng ký
@app.route("/register.html", methods=["GET"])
def serve_register():
    return send_from_directory(FRONTEND_DIR, "register.html")


# Trang Chat
@app.route("/index.html", methods=["GET"])
def serve_index():
    return send_from_directory(FRONTEND_DIR, "index.html")


# Các file CSS, JS, IMG...
@app.route("/<path:path>", methods=["GET"])
def serve_frontend(path):
    file_path = os.path.join(FRONTEND_DIR, path)

    if os.path.isfile(file_path):
        return send_from_directory(FRONTEND_DIR, path)

    abort(404)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))

    print("=" * 50)
    print(f"Server running at: http://127.0.0.1:{port}")
    print(f"Login page      : http://127.0.0.1:{port}/")
    print(f"Chat page       : http://127.0.0.1:{port}/index.html")
    print("=" * 50)

    app.run(host="0.0.0.0", port=port, debug=False)
