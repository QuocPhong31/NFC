from flask import Flask, send_from_directory, render_template, redirect, session, request
from flask_cors import CORS
from config import get_connection

from admin import admin_bp
from user import user_bp
from card import card_bp
import os

app = Flask(__name__)
app.secret_key = "nfc_secret_key"
app.register_blueprint(card_bp)

CORS(
    app,
    supports_credentials=True,
    resources={
        r"/api/*": {
            "origins": [
                "https://nfc.thanhtamtraquan.com",
                "https://quocphong31.github.io",
                "https://shop.thanhtamtraquan.com",
                "http://127.0.0.1:5500",
                "http://localhost:5500"
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    }
)

# Đường dẫn tới thư mục chứa frontend
STATIC_DIR = os.path.join(os.path.dirname(__file__), "web")

# API cho user (bạn đang dùng)
# app.register_blueprint(public_bp) 88888

# Admin routes
app.register_blueprint(admin_bp)
app.register_blueprint(user_bp)


@app.get("/")
def home():
    return "API chạy OK + Admin OK"

# def has_pending_order():
#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.execute(
#         "SELECT 1 FROM donthanhtoan WHERE trangThai = 'choXacNhan' LIMIT 1"
#     )
#     result = cursor.fetchone()
#     cursor.close()
#     conn.close()
#     return result is not None


# @app.post("/api/track-view")
# def track_view():
#     ip = request.headers.get("X-Forwarded-For", request.remote_addr)
#     if ip:
#         ip = ip.split(",")[0].strip()
#
#     conn = get_connection()
#     cur = conn.cursor()
#     cur.execute(
#         "INSERT INTO truycap_logs (ip_address) VALUES (%s)",
#         (ip,)
#     )
#     conn.commit()
#     cur.close()
#     conn.close()
#
#     return {"ok": True}

# Khi truy cập /admin/ cần phải có session admin, nếu chưa => redirect /admin/login
@app.get("/admin/")
def admin_page():
    if not session.get("admin"):
        return redirect("/admin/login")
    # truyền admin từ session vào template (để Jinja có biến admin)
    return render_template("admin/index.html", admin=session.get("admin"))

# @app.route('/images/<path:filename>')
# def serve_image(filename):
#     # image dir là backend_py/image
#     image_dir = os.path.join(app.root_path, 'image')
#     return send_from_directory(image_dir, filename)
#
# # Serve trang product (1 file dùng chung)
# @app.route("/product/<int:id>")
# def product_page(id):
#     return send_from_directory(os.path.join(STATIC_DIR, "Product"), "product.html")

# Serve tất cả file tĩnh còn lại (CSS, JS, images,...)
@app.route("/<path:path>")
def static_proxy(path):
    return send_from_directory(STATIC_DIR, path)

if __name__ == "__main__":
    app.run(debug=True)
