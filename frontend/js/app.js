const username = localStorage.getItem("username");
const token = getToken();
if (!username || !token) window.location.href = "login.html";

const chat = document.getElementById("chat");
const input = document.getElementById("input");

let sessionId = crypto.randomUUID();
let mode = localStorage.getItem("mode") || "ai";
let isSending = false;

const EMPTY_STATE_HTML = `
    <div id="empty-state" class="empty-state">
        <div class="empty-visual">
            <div class="orb orb-1"></div>
            <div class="orb orb-2"></div>
            <div class="empty-card">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
            </div>
        </div>
        <h2>Xin chào!</h2>
        <p>Hỏi bất cứ điều gì — AI sẽ trả lời ngay, hoặc chuyển sang Knowledge để tra cứu dữ liệu.</p>
        <div class="suggestions">
            <button class="suggestion" onclick="useSuggestion('Xin chào, bạn có thể giúp gì?')">Xin chào 👋</button>
            <button class="suggestion" onclick="useSuggestion('Giá sản phẩm bao nhiêu?')">Hỏi giá 💰</button>
            <button class="suggestion" onclick="useSuggestion('Chính sách giao hàng thế nào?')">Giao hàng 📦</button>
        </div>
    </div>
`;

function setMode(m) {
    mode = m;
    localStorage.setItem("mode", m);

    document.getElementById("btn-ai")?.classList.toggle("active", m === "ai");
    document.getElementById("btn-data")?.classList.toggle("active", m === "data");

    const badge = document.getElementById("mode-badge");
    if (badge) badge.textContent = m === "ai" ? "AI" : "Data";
}

function useSuggestion(text) {
    input.value = text;
    autoResizeInput();
    input.focus();
    sendMessage();
}

function autoResizeInput() {
    input.style.height = "auto";
    input.style.height = Math.min(input.scrollHeight, 160) + "px";
}

function addMessage(text, type) {
    if (!text) return;

    document.getElementById("empty-state")?.remove();

    const wrapper = document.createElement("div");
    wrapper.className = `msg-wrapper ${type}`;

    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.textContent = type === "user" ? username.charAt(0).toUpperCase() : "AI";

    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.textContent = text;

    wrapper.append(avatar, bubble);
    chat.appendChild(wrapper);
    chat.scrollTop = chat.scrollHeight;
}

function showTyping() {
    const div = document.createElement("div");
    div.className = "msg-wrapper bot";
    div.id = "typing";
    div.innerHTML = `
        <div class="avatar">AI</div>
        <div class="bubble typing-bubble">
            <span class="dot"></span><span class="dot"></span><span class="dot"></span>
        </div>
    `;
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
}

function removeTyping() {
    document.getElementById("typing")?.remove();
}

async function sendMessage() {
    const text = input.value.trim();
    if (!text || isSending) return;

    isSending = true;
    input.disabled = true;
    document.querySelector(".send-btn")?.setAttribute("disabled", "");

    addMessage(text, "user");
    input.value = "";
    autoResizeInput();
    showTyping();

    try {
        const data = await apiPost("/chat", {
            text,
            session_id: sessionId,
            mode,
        });

        removeTyping();

        if (!data?.reply) {
            addMessage("Không có phản hồi từ server", "bot");
            return;
        }

        addMessage(data.reply, "bot");
    } catch {
        removeTyping();
        addMessage("Lỗi kết nối server. Hãy kiểm tra backend đang chạy.", "bot");
    } finally {
        isSending = false;
        input.disabled = false;
        document.querySelector(".send-btn")?.removeAttribute("disabled");
        input.focus();
    }
}

function newChat() {
    chat.innerHTML = EMPTY_STATE_HTML;
    sessionId = crypto.randomUUID();
}

async function loadHistory() {
    try {
        const data = await apiGet("/history");

        if (!Array.isArray(data) || data.length === 0) {
            newChat();
            return;
        }

        chat.innerHTML = "";
        data.forEach((item) => {
            if (item.user) addMessage(item.user, "user");
            if (item.bot) addMessage(item.bot, "bot");
        });
    } catch {
        newChat();
    }
}

function logout() {
    localStorage.removeItem("username");
    localStorage.removeItem("token");
    localStorage.removeItem("mode");
    window.location.href = "login.html";
}

input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

input.addEventListener("input", autoResizeInput);

document.addEventListener("DOMContentLoaded", () => {
    const userDisplay = document.getElementById("username-display");
    if (userDisplay) userDisplay.textContent = username;

    const avatarEl = document.getElementById("user-avatar");
    if (avatarEl) avatarEl.textContent = username.charAt(0).toUpperCase();

    setMode(mode);
    loadHistory();
    autoResizeInput();
});
