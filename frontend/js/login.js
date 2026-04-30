async function login() {
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();

    if (!username || !password) {
        alert("Vui lòng nhập đầy đủ");
        return;
    }

    try {
        const res = await fetch("http://127.0.0.1:5000/login", {
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
            // 🔥 lưu user
            localStorage.setItem("username", username);

            // chuyển sang chat
            window.location.href = "index.html";
        } else {
            alert(data.msg);
        }

    } catch (err) {
        alert("❌ Lỗi server");
        console.error(err);
    }
}