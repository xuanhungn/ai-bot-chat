// ===== CHECK LOGIN =====
const username = localStorage.getItem("username");

if (!username) {
    window.location.href = "login.html";
}

// ===== DOM =====
const chat = document.getElementById("chat");
const input = document.getElementById("input");

const session_id = Math.random().toString(36).substring(2);

// ===== MODE =====
let mode = localStorage.getItem("mode") || "ai"; // 🔥 load mode

// ===== SET MODE =====
function setMode(m) {
    mode = m;

    // 🔥 lưu lại
    localStorage.setItem("mode", m);

    const btnAI = document.getElementById("btn-ai");
    const btnData = document.getElementById("btn-data");

    if (!btnAI || !btnData) return;

    btnAI.classList.remove("active");
    btnData.classList.remove("active");

    if (m === "ai") {
        btnAI.classList.add("active");
    } else {
        btnData.classList.add("active");
    }

    console.log("MODE:", mode);
}

// ===== UI CHAT =====
function addMessage(text, type) {
    if (!text) return;

    const wrapper = document.createElement("div");
    wrapper.className = "msg-wrapper " + type;

    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.innerText = type === "user" ? "🧑" : "🤖";

    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.innerText = text;

    if (type === "user") {
        wrapper.appendChild(bubble);
        wrapper.appendChild(avatar);
    } else {
        wrapper.appendChild(avatar);
        wrapper.appendChild(bubble);
    }

    chat.appendChild(wrapper);
    chat.scrollTop = chat.scrollHeight;
}

// ===== TYPING =====
function showTyping() {
    const div = document.createElement("div");
    div.className = "msg-wrapper bot";
    div.id = "typing";

    div.innerHTML = `
        <div class="avatar">🤖</div>
        <div class="bubble">Đang trả lời...</div>
    `;

    chat.appendChild(div);
}

function removeTyping() {
    const t = document.getElementById("typing");
    if (t) t.remove();
}

// ===== SEND =====
async function sendMessage() {
    const text = input.value.trim();
    if (!text) return;

    addMessage(text, "user");
    input.value = "";

    showTyping();

    try {
        console.log("ĐANG GỬI MODE:", mode); // 🔥 debug

        const res = await fetch("http://127.0.0.1:5000/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                text: text,
                session_id: session_id,
                mode: mode,
                username: username
            })
        });

        const data = await res.json();

        console.log("API RESPONSE:", data);

        removeTyping();

        if (!data || !data.reply) {
            addMessage("❌ Không có phản hồi từ server", "bot");
            return;
        }

        addMessage(data.reply, "bot");

    } catch (err) {
        removeTyping();
        addMessage("❌ Lỗi server", "bot");
        console.error("SEND ERROR:", err);
    }
}

// ===== NEW CHAT =====
function newChat() {
    chat.innerHTML = "";
}

// ===== LOAD HISTORY =====
async function loadHistory() {
    try {
        const res = await fetch(
            `http://127.0.0.1:5000/history?username=${username}`
        );

        const text = await res.text();

        let data;
        try {
            data = JSON.parse(text);
        } catch {
            console.error("❌ Response không phải JSON:", text);
            return;
        }

        console.log("HISTORY:", data);

        if (!Array.isArray(data)) {
            console.error("❌ History không phải array:", data);
            return;
        }

        chat.innerHTML = "";

        data.forEach(item => {
            if (item.user) addMessage(item.user, "user");
            if (item.bot) addMessage(item.bot, "bot");
        });

    } catch (err) {
        console.error("❌ Lỗi load history:", err);
    }
}

// ===== LOGOUT =====
function logout() {
    localStorage.removeItem("username");
    localStorage.removeItem("mode"); // 🔥 reset mode luôn
    window.location.href = "login.html";
}

// ===== LOAD PAGE =====
window.onload = () => {
    loadHistory();

    // 🔥 set lại UI đúng mode
    setMode(mode);
};

// ===== ENTER SEND =====
input.addEventListener("keypress", function(e) {
    if (e.key === "Enter") {
        sendMessage();
    }
});

// ===== HIỂN THỊ USERNAME =====
window.addEventListener("DOMContentLoaded", () => {
    const userDisplay = document.getElementById("username-display");
    if (userDisplay && username) {
        userDisplay.innerText = "👤 " + username;
    }
});