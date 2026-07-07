async function login() {
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;
    const btn = document.querySelector(".btn-primary");
    const errorEl = document.getElementById("error-msg");

    errorEl.textContent = "";

    if (!username || !password) {
        errorEl.textContent = "Vui lòng nhập đầy đủ thông tin";
        return;
    }

    btn.disabled = true;
    btn.textContent = "Đang đăng nhập...";

    try {
        const data = await apiPost("/login", { username, password });

        if (data.msg?.includes("thành công") && data.token) {
            localStorage.setItem("username", data.username || username);
            localStorage.setItem("token", data.token);
            window.location.href = "index.html";
        } else {
            errorEl.textContent = data.msg || "Đăng nhập thất bại";
        }
    } catch (err) {
        errorEl.textContent = err.message || "Không thể kết nối server";
        console.error("Login error:", err);
    } finally {
        btn.disabled = false;
        btn.textContent = "Đăng nhập";
    }
}

document.getElementById("password")?.addEventListener("keydown", (e) => {
    if (e.key === "Enter") login();
});
