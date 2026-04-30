async function register() {
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();

    if (!username || !password) {
        alert("Vui lòng nhập đầy đủ");
        return;
    }

    if (password.length < 4) {
        alert("Mật khẩu tối thiểu 4 ký tự");
        return;
    }

    try {
        const res = await fetch("http://127.0.0.1:5000/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        });

        const data = await res.json();

        if (data.msg.includes("thành công")) {
            alert("✅ Đăng ký thành công!");

            // 👉 chuyển sang login
            window.location.href = "login.html";
        } else {
            alert(data.msg);
        }

    } catch (err) {
        alert("❌ Lỗi server");
        console.error(err);
    }
}