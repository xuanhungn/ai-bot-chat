# Nova — AI Chat

Chat AI + Knowledge Base. **Code lưu trên GitHub**, **chạy local** bằng backend trong VS Code.

## Chạy app (chỉ cần backend)

Backend tự phục vụ luôn giao diện frontend — không cần Live Server, không cần deploy.

### Cách 1 — VS Code (khuyên dùng)

1. Mở thư mục dự án trong VS Code
2. `Ctrl+Shift+B` hoặc **Terminal → Run Build Task** → **Nova: Chạy Backend**
3. Hoặc **Run and Debug** (`F5`) → chọn **Nova: Backend API**
4. Mở trình duyệt: **http://127.0.0.1:5000/login.html**

### Cách 2 — Terminal

```bash
pip install -r requirements.txt
cp .env.example .env
# Sửa .env: thêm GROQ_API_KEY từ https://console.groq.com

cd backend
python api.py
```

## Đẩy toàn bộ lên GitHub (chỉ lưu code)

GitHub **không chạy** app Flask — chỉ lưu source code. Bạn vẫn chạy local như trên.

```powershell
cd "Z:\ai bot chat"
git init
git add .
git commit -m "Nova AI Chat"
git branch -M main
```

Tạo repo trống tại https://github.com/new rồi:

```powershell
git remote add origin https://github.com/TEN_USER/nova-ai-chat.git
git push -u origin main
```

Link repo: `https://github.com/TEN_USER/nova-ai-chat`

> File `.env` **không** lên GitHub (có API key). Các file khác đều push được.

## Cấu trúc

```
backend/api.py    ← chạy file này
frontend/         ← HTML/CSS/JS (backend tự serve)
data/             ← users, history, knowledge base
.env              ← cấu hình local (không push)
```

## Clone máy khác

```bash
git clone https://github.com/TEN_USER/nova-ai-chat.git
cd nova-ai-chat
pip install -r requirements.txt
cp .env.example .env
# điền GROQ_API_KEY vào .env
cd backend && python api.py
```

## Deploy backend lên Render (để dùng với Vercel)

1. Push code mới nhất lên GitHub.
2. Vào [render.com](https://render.com) -> **New** -> **Blueprint** -> chọn repo này.
3. Render sẽ đọc file `render.yaml` và tạo web service backend.
4. Sau khi deploy xong, copy URL backend dạng:
   - `https://ten-service.onrender.com`
5. Mở `frontend/js/config.js`, thay dòng:
   - `https://RENDER_BACKEND_URL.onrender.com`
   bằng URL thật của Render backend.
6. Push lại lên GitHub để Vercel tự deploy frontend mới.

Lưu ý: frontend Vercel và backend Render phải dùng URL public, backend local trong VS Code không phục vụ được cho link Vercel.
