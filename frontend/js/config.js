const API_BASE = (() => {
    const { protocol, hostname, port, origin } = window.location;

    if (protocol === "file:" || !hostname) {
        return "http://127.0.0.1:5000";
    }

    // Production: frontend + API cùng domain (Render, VPS, ...)
    if (!port || port === "443" || port === "80") {
        return origin;
    }

    if (port === "5000") {
        return origin;
    }

    if (hostname === "127.0.0.1" || hostname === "localhost") {
        return "http://127.0.0.1:5000";
    }

    return origin;
})();

function getToken() {
    return localStorage.getItem("token");
}

function authHeaders() {
    const headers = { "Content-Type": "application/json" };
    const token = getToken();
    if (token) headers.Authorization = `Bearer ${token}`;
    return headers;
}

function handleUnauthorized() {
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    if (!window.location.pathname.endsWith("login.html") &&
        !window.location.pathname.endsWith("register.html")) {
        window.location.href = "login.html";
    }
}

async function parseResponse(res) {
    const text = await res.text();
    try {
        return JSON.parse(text);
    } catch {
        throw new Error(`Server lỗi (${res.status}). Hãy khởi động lại backend.`);
    }
}

async function apiPost(endpoint, body) {
    let res;
    try {
        res = await fetch(`${API_BASE}${endpoint}`, {
            method: "POST",
            headers: authHeaders(),
            body: JSON.stringify(body),
        });
    } catch {
        throw new Error(
            "Không kết nối được server. Hãy chạy: cd backend → python api.py, rồi mở http://127.0.0.1:5000/login.html"
        );
    }

    const data = await parseResponse(res);

    if (res.status === 401) {
        handleUnauthorized();
        throw new Error(data.msg || "Phien dang nhap het han");
    }

    return data;
}

async function apiGet(endpoint) {
    let res;
    try {
        res = await fetch(`${API_BASE}${endpoint}`, {
            headers: authHeaders(),
        });
    } catch {
        throw new Error(
            "Không kết nối được server. Hãy chạy: cd backend → python api.py"
        );
    }

    const data = await parseResponse(res);

    if (res.status === 401) {
        handleUnauthorized();
        throw new Error(data.msg || "Phien dang nhap het han");
    }

    return data;
}
