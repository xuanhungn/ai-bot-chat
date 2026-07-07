async function register() {
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;
    const btn = document.querySelector(".btn-primary");
    const errorEl = document.getElementById("error-msg");

    errorEl.textContent = "";

    if (!username || !password) {
        errorEl.textContent = "Vui lòng nhập đầy đủ thông tin";
        return;
    }

    if (password.length < 4) {
        errorEl.textContent = "Mật khẩu tối thiểu 4 ký tự";
        return;
    }

    btn.disabled = true;
    btn.textContent = "Đang đăng ký...";

    try {
        const data = await apiPost("/register", { username, password });

        if (data.msg?.includes("thành công")) {
            window.location.href = "login.html";
        } else {
            errorEl.textContent = data.msg || "Đăng ký thất bại";
        }
    } catch (err) {
        errorEl.textContent = err.message || "Không thể kết nối server";
        console.error("Register error:", err);
    } finally {
        btn.disabled = false;
        btn.textContent = "Tạo tài khoản";
    }
}

document.getElementById("password")?.addEventListener("keydown", (e) => {
    if (e.key === "Enter") register();
});
