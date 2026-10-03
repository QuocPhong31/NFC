from flask import Blueprint, request, jsonify, session
from config import get_connection
from utils import hash_password

user_bp = Blueprint("users", __name__)

# Lấy danh sách user
@user_bp.get("/admin/users")
def get_users():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM nguoidungs")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(data)

# Tạo user mới
@user_bp.post("/admin/users")
def create_user():
    # nhận JSON body
    d = request.get_json(force=True)   # auto parse JSON

    # validate bắt buộc
    if not d.get("taiKhoan") or not d.get("matKhau"):
        return jsonify({"msg": "Thiếu tài khoản hoặc mật khẩu"}), 400

    # role hợp lệ (mặc định USER)
    role = (d.get("role") or "USER").upper()
    if role not in ("ADMIN", "USER"):
        role = "USER"

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO nguoidungs 
                (hoTen, gioiTinh, ngaySinh, diaChi, SDT, email, taiKhoan, matKhau, role)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            d.get("hoTen"),
            d.get("gioiTinh"),
            d.get("ngaySinh"),
            d.get("diaChi"),
            d.get("SDT"),
            d.get("email"),
            d.get("taiKhoan"),
            hash_password(d.get("matKhau")),
            role
        ))

        conn.commit()
        return jsonify({"msg": "Tạo user thành công"})

    except Exception as ex:
        print("Create user error:", ex)
        return jsonify({"msg": "Lỗi khi tạo user", "error": str(ex)}), 500

    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass

# XÓA user (hard delete)
@user_bp.delete("/admin/users/<int:id>")
def admin_delete_user(id):
    # kiểm tra đã login là admin
    if not session.get("admin"):
        return jsonify({"msg":"Không có quyền"}), 403

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM nguoidungs WHERE id=%s", (id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"msg":"Xóa người dùng thành công"})
    except Exception as ex:
        # trả lỗi rõ để frontend hiển thị (vd: constraint)
        return jsonify({"msg":"Lỗi khi xóa user", "error": str(ex)}), 500