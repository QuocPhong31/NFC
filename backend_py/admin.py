from flask import Blueprint, request, jsonify, render_template, session, redirect
from config import get_connection
from utils import hash_password

admin_bp = Blueprint("admin", __name__)

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

# trang login (form)
@admin_bp.get("/admin/login")
def admin_login_page():
    return render_template("login.html")

# xử lý login (hỗ trợ form hoặc json)
@admin_bp.route("/admin/login", methods=["POST"])
def admin_login():
    # Nếu client gửi JSON (ví dụ fetch), dùng request.json
    if request.is_json:
        data = request.get_json()
        username = data.get("username")
        password = hash_password(data.get("password") or "")
    else:
        # form submit từ login.html
        username = request.form.get("username")
        password = hash_password(request.form.get("password") or "")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM nguoidungs WHERE taiKhoan=%s AND matKhau=%s AND role='ADMIN'",
                   (username, password))
    admin = cursor.fetchone()

    cursor.close()
    conn.close()

    if admin:
        # Lưu một vài thông tin cần thiết vào session
        session["admin"] = {
            "id": admin["id"],
            "taiKhoan": admin.get("taiKhoan"),
            "hoTen": admin.get("hoTen")
        }

        # nếu request là form, redirect về /admin/, nếu ajax/json trả JSON
        if request.is_json:
            return jsonify({"msg": "Đăng nhập thành công", "admin": session["admin"]})
        else:
            return redirect("/admin/")
    # login thất bại
    if request.is_json:
        return jsonify({"msg": "Sai tài khoản hoặc mật khẩu"}), 400
    else:
        return render_template("login.html", error="Sai tài khoản hoặc mật khẩu")

# logout
@admin_bp.get("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect("/admin/login")

@admin_bp.route("/admin/users-page")
def admin_users_page():
    if not session.get("admin"):
        return redirect("/admin/login")
    return render_template("admin/user.html", admin=session.get("admin"))

