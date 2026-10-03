from flask import Blueprint, request, jsonify, session, render_template, redirect
from config import get_connection

from qr_service import create_qr
from slug_service import generate_slug
from cloudinary_service import upload_image

import os


card_bp = Blueprint("cards", __name__)


# =========================================================
# HELPER
# =========================================================

def require_admin():
    """
    Kiểm tra admin đã đăng nhập chưa.
    """
    return session.get("admin")


def get_owned_card(card_id, user_id):
    """
    Lấy card nếu card thuộc user hiện tại.
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT *
        FROM the_nfc
        WHERE id=%s
        AND user_id=%s
    """, (
        card_id,
        user_id
    ))

    card = cur.fetchone()

    cur.close()
    conn.close()

    return card


# =========================================================
# GET ALL CARDS
# GET /api/cards
# =========================================================
@card_bp.get("/admin/cards/<int:card_id>/edit")
def edit_card_page(card_id):

    admin = session.get("admin")

    if not admin:
        return redirect("/admin/login")

    conn = None
    cur = None

    try:

        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        # ==============================
        # CARD
        # ==============================

        cur.execute("""
            SELECT *
            FROM the_nfc
            WHERE id=%s
              AND user_id=%s
        """, (
            card_id,
            admin["id"]
        ))

        card = cur.fetchone()

        if not card:
            return "Không tìm thấy thẻ", 404

        # ==============================
        # CARD ITEMS
        # ==============================

        cur.execute("""
            SELECT
                id,
                card_id,
                category,
                platform,
                item_type,
                display_title,
                value,
                sort_order,
                is_active
            FROM card_items
            WHERE card_id=%s
              AND is_active=TRUE
            ORDER BY sort_order, id
        """, (card_id,))

        card_items = cur.fetchall()

        # ==============================
        # CERTIFICATES
        # ==============================

        cur.execute("""
            SELECT *
            FROM card_certificates
            WHERE card_id=%s
              AND is_active=TRUE
            ORDER BY sort_order, id
        """, (card_id,))

        certificates = cur.fetchall()

        # ==============================
        # PUBLIC URL
        # ==============================

        base_url = (
            os.getenv("PUBLIC_BASE_URL")
            or "http://127.0.0.1:5500"
        )

        public_url = f"{base_url}/#/p/{card['slug']}"

        return render_template(
            "admin/edit_card.html",
            card=card,
            card_items=card_items,
            certificates=certificates,
            admin=admin,
            public_url=public_url
        )

    except Exception as ex:

        print("EDIT CARD PAGE ERROR:")
        print(ex)

        return (
            "Lỗi khi mở trang chỉnh sửa: " + str(ex),
            500
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

@card_bp.get("/api/cards")
def get_cards():

    admin = session.get("admin")

    if not admin:
        return jsonify({
            "msg": "Không có quyền"
        }), 403

    user_id = admin["id"]

    conn = None
    cur = None

    try:

        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        # =====================================================
        # 1. LẤY DANH SÁCH CARD
        # =====================================================

        cur.execute("""
            SELECT *
            FROM the_nfc
            WHERE user_id=%s
            ORDER BY id DESC
        """, (user_id,))

        cards = cur.fetchall()

        # =====================================================
        # 2. LẤY TẤT CẢ CARD ITEMS CỦA CÁC CARD
        # =====================================================

        if cards:

            card_ids = [
                card["id"]
                for card in cards
            ]

            placeholders = ",".join(
                ["%s"] * len(card_ids)
            )

            cur.execute(f"""
                SELECT
                    id,
                    card_id,
                    category,
                    platform,
                    item_type,
                    display_title,
                    value,
                    sort_order,
                    is_active
                FROM card_items
                WHERE card_id IN ({placeholders})
                  AND is_active=TRUE
                ORDER BY sort_order, id
            """, tuple(card_ids))

            items = cur.fetchall()

        else:

            items = []

        # =====================================================
        # 3. GROUP ITEMS THEO CARD
        # =====================================================

        items_by_card = {}

        for item in items:

            card_id = item["card_id"]

            if card_id not in items_by_card:
                items_by_card[card_id] = []

            items_by_card[card_id].append(item)

        # =====================================================
        # 4. GẮN ITEMS VÀO CARD
        # =====================================================

        for card in cards:

            card["items"] = items_by_card.get(
                card["id"],
                []
            )

        return jsonify(cards)

    except Exception as ex:

        print("================================")
        print("GET CARDS ERROR:")
        print(ex)
        print("================================")

        return jsonify({
            "msg": "Không thể lấy danh sách thẻ",
            "error": str(ex)
        }), 500

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

# =========================================================
# CREATE CARD
# POST /api/cards
# =========================================================

@card_bp.post("/api/cards")
def create_card():

    admin = require_admin()

    if not admin:
        return jsonify({
            "msg": "Không có quyền"
        }), 403


    data = request.get_json(
        silent=True
    ) or {}


    user_id = admin["id"]


    ten_the = (
        data.get("tenThe")
        or ""
    ).strip()


    if not ten_the:

        return jsonify({
            "msg": "Thiếu tên thẻ"
        }), 400


    slug = generate_slug(
        ten_the
    )


    try:

        conn = get_connection()
        cur = conn.cursor()


        cur.execute("""
            INSERT INTO the_nfc (
                user_id,
                tenThe,
                slug,
                hoTen,
                chucVu,
                congTy,
                phongBan,
                gioiThieu,
                email,
                soDienThoai,
                urlCongTy,
                diaChi,
                maSoThue,
                theme
            )
            VALUES (
                %s,%s,%s,%s,%s,%s,%s,
                %s,%s,%s,%s,%s,%s,%s
            )
        """, (
            user_id,
            ten_the,
            slug,

            data.get("hoTen"),
            data.get("chucVu"),
            data.get("congTy"),
            data.get("phongBan"),
            data.get("gioiThieu"),

            data.get("email"),
            data.get("soDienThoai"),
            data.get("urlCongTy"),
            data.get("diaChi"),
            data.get("maSoThue"),

            data.get(
                "theme",
                "#ff8a00"
            )
        ))


        card_id = cur.lastrowid


        conn.commit()


        cur.close()
        conn.close()


        # =================================================
        # TẠO PUBLIC URL
        # =================================================

        base_url = (
            os.getenv(
                "PUBLIC_BASE_URL"
            )
            or "http://127.0.0.1:5500"
        )


        public_url = (
            f"{base_url}/#/p/{slug}"
        )


        # =================================================
        # TẠO QR
        # =================================================

        qr_url = create_qr(
            public_url,
            f"card_{card_id}"
        )


        # =================================================
        # UPDATE QR
        # =================================================

        conn = get_connection()
        cur = conn.cursor()


        cur.execute("""
            UPDATE the_nfc
            SET qrUrl=%s
            WHERE id=%s
        """, (
            qr_url,
            card_id
        ))


        conn.commit()


        cur.close()
        conn.close()


        return jsonify({

            "msg":
                "Tạo thẻ thành công",

            "cardId":
                card_id,

            "slug":
                slug,

            "url":
                public_url,

            "qrUrl":
                qr_url

        }), 201


    except Exception as ex:

        print(
            "Create card error:",
            ex
        )

        return jsonify({

            "msg":
                "Tạo thẻ thất bại",

            "error":
                str(ex)

        }), 500


# =========================================================
# GET ONE CARD
# GET /api/cards/<id>
# =========================================================

@card_bp.get("/api/cards/<int:card_id>")
def get_card(card_id):

    admin = require_admin()

    if not admin:

        return jsonify({
            "msg": "Không có quyền"
        }), 403


    user_id = admin["id"]


    try:

        conn = get_connection()
        cur = conn.cursor(
            dictionary=True
        )


        # =================================================
        # CARD
        # =================================================

        cur.execute("""
            SELECT *
            FROM the_nfc
            WHERE id=%s
            AND user_id=%s
        """, (
            card_id,
            user_id
        ))


        card = cur.fetchone()


        if not card:

            cur.close()
            conn.close()

            return jsonify({
                "msg":
                    "Không tìm thấy thẻ"
            }), 404


        # =================================================
        # LINKS
        # =================================================

        cur.execute("""
            SELECT *
            FROM card_items
            WHERE card_id=%s
            AND is_active=TRUE
            ORDER BY sort_order
        """, (
            card_id,
        ))


        links = cur.fetchall()


        # =================================================
        # CERTIFICATES
        # =================================================

        cur.execute("""
            SELECT *
            FROM card_certificates
            WHERE card_id=%s
            AND is_active=TRUE
            ORDER BY sort_order
        """, (
            card_id,
        ))


        certificates = (
            cur.fetchall()
        )


        cur.close()
        conn.close()


        card["links"] = links

        card["certificates"] = (
            certificates
        )


        return jsonify(card)


    except Exception as ex:

        print(
            "Get card error:",
            ex
        )

        return jsonify({

            "msg":
                "Không thể lấy thông tin thẻ",

            "error":
                str(ex)

        }), 500


# =========================================================
# UPDATE CARD
# PUT /api/cards/<id>
# =========================================================

@card_bp.put("/api/cards/<int:card_id>")
def update_card(card_id):

    admin = require_admin()

    if not admin:
        return jsonify({
            "msg": "Không có quyền"
        }), 403


    user_id = admin["id"]


    # =====================================================
    # CHECK CARD
    # =====================================================

    card = get_owned_card(
        card_id,
        user_id
    )


    if not card:

        return jsonify({
            "msg": "Không tìm thấy thẻ"
        }), 404


    try:

        # =================================================
        # TEXT DATA
        # =================================================

        ten_the = request.form.get(
            "tenThe",
            card["tenThe"]
        )

        ho_ten = request.form.get(
            "hoTen",
            card["hoTen"]
        )

        chuc_vu = request.form.get(
            "chucVu",
            card["chucVu"]
        )

        cong_ty = request.form.get(
            "congTy",
            card["congTy"]
        )

        phong_ban = request.form.get(
            "phongBan",
            card["phongBan"]
        )

        gioi_thieu = request.form.get(
            "gioiThieu",
            card["gioiThieu"]
        )

        email = request.form.get(
            "email",
            card["email"]
        )

        so_dien_thoai = request.form.get(
            "soDienThoai",
            card["soDienThoai"]
        )

        url_cong_ty = request.form.get(
            "urlCongTy",
            card["urlCongTy"]
        )

        dia_chi = request.form.get(
            "diaChi",
            card["diaChi"]
        )

        ma_so_thue = request.form.get(
            "maSoThue",
            card["maSoThue"]
        )

        theme = request.form.get(
            "theme",
            card["theme"]
        )


        # =================================================
        # IMAGE URL
        # Giữ ảnh cũ nếu user không chọn ảnh mới
        # =================================================

        anh_bia = card["anhBia"]

        anh_dai_dien = card["anhDaiDien"]

        logo = card["logo"]


        # =================================================
        # COVER
        # =================================================

        cover_file = request.files.get(
            "anhBia"
        )


        if cover_file and cover_file.filename:

            result = upload_image(
                cover_file,
                folder=f"nfc/cards/{card_id}",
                public_id="cover"
            )

            anh_bia = result["url"]


        # =================================================
        # AVATAR
        # =================================================

        avatar_file = request.files.get(
            "anhDaiDien"
        )


        if avatar_file and avatar_file.filename:

            result = upload_image(
                avatar_file,
                folder=f"nfc/cards/{card_id}",
                public_id="avatar"
            )

            anh_dai_dien = result["url"]


        # =================================================
        # LOGO
        # =================================================

        logo_file = request.files.get(
            "logo"
        )


        if logo_file and logo_file.filename:

            result = upload_image(
                logo_file,
                folder=f"nfc/cards/{card_id}",
                public_id="logo"
            )

            logo = result["url"]


        # =================================================
        # UPDATE DATABASE
        # =================================================

        conn = get_connection()

        cur = conn.cursor()


        cur.execute("""
            UPDATE the_nfc
            SET
                tenThe=%s,
                hoTen=%s,
                chucVu=%s,
                congTy=%s,
                phongBan=%s,
                gioiThieu=%s,
                email=%s,
                soDienThoai=%s,
                urlCongTy=%s,
                diaChi=%s,
                maSoThue=%s,
                anhBia=%s,
                anhDaiDien=%s,
                logo=%s,
                theme=%s
            WHERE id=%s
            AND user_id=%s
        """, (

            ten_the,
            ho_ten,
            chuc_vu,
            cong_ty,
            phong_ban,
            gioi_thieu,
            email,
            so_dien_thoai,
            url_cong_ty,
            dia_chi,
            ma_so_thue,

            anh_bia,
            anh_dai_dien,
            logo,

            theme,

            card_id,
            user_id
        ))


        conn.commit()


        cur.close()
        conn.close()


        return jsonify({

            "msg": "Lưu thay đổi thành công",

            "cardId": card_id,

            "anhBia": anh_bia,

            "anhDaiDien": anh_dai_dien,

            "logo": logo

        })


    except Exception as ex:

        print("================================")
        print("UPDATE CARD ERROR:")
        print(ex)
        print("================================")


        return jsonify({

            "msg": "Lưu thay đổi thất bại",

            "error": str(ex)

        }), 500

# =========================================================
# DELETE CARD
# DELETE /api/cards/<id>
# =========================================================

@card_bp.delete("/api/cards/<int:card_id>")
def delete_card(card_id):

    admin = require_admin()

    if not admin:

        return jsonify({
            "msg": "Không có quyền"
        }), 403


    user_id = admin["id"]


    try:

        conn = get_connection()
        cur = conn.cursor()


        cur.execute("""
            DELETE FROM the_nfc
            WHERE id=%s
            AND user_id=%s
        """, (
            card_id,
            user_id
        ))


        if cur.rowcount == 0:

            conn.rollback()

            cur.close()
            conn.close()

            return jsonify({
                "msg":
                    "Không tìm thấy thẻ"
            }), 404


        conn.commit()


        cur.close()
        conn.close()


        return jsonify({

            "msg":
                "Xóa thẻ thành công"

        })


    except Exception as ex:

        print(
            "Delete card error:",
            ex
        )

        return jsonify({

            "msg":
                "Xóa thẻ thất bại",

            "error":
                str(ex)

        }), 500


# =========================================================
# PUBLIC CARD
# GET /api/public/cards/<slug>
# =========================================================

# =========================================================
# PUBLIC CARD
# GET /api/public/cards/<slug>
# =========================================================

@card_bp.get("/api/public/cards/<slug>")
def public_card(slug):

    conn = None
    cur = None

    try:
        # -------------------------------------------------
        # Chuẩn hóa slug
        # -------------------------------------------------
        slug = slug.strip()

        print("========================================")
        print("PUBLIC CARD REQUEST")
        print("Slug nhận được:", repr(slug))
        print("========================================")

        conn = get_connection()

        # Kiểm tra database hiện tại
        check_cur = conn.cursor()
        check_cur.execute("SELECT DATABASE()")
        current_db = check_cur.fetchone()
        check_cur.close()

        print("Database hiện tại:", current_db)

        cur = conn.cursor(dictionary=True)

        # -------------------------------------------------
        # Lấy card
        # -------------------------------------------------

        cur.execute("""
            SELECT
                id,
                user_id,
                tenThe,
                slug,
                hoTen,
                chucVu,
                congTy,
                phongBan,
                gioiThieu,
                email,
                soDienThoai,
                urlCongTy,
                diaChi,
                maSoThue,
                anhBia,
                anhDaiDien,
                logo,
                theme,
                qrUrl,
                trangThai
            FROM the_nfc
            WHERE TRIM(slug) = %s
            LIMIT 1
        """, (slug,))

        card = cur.fetchone()

        print("CARD TÌM ĐƯỢC:")
        print(card)

        # -------------------------------------------------
        # Không tìm thấy slug
        # -------------------------------------------------

        if not card:
            return jsonify({
                "msg": "Không tìm thấy profile",
                "slug": slug
            }), 404

        # -------------------------------------------------
        # Kiểm tra trạng thái
        # -------------------------------------------------

        if card["trangThai"] != "ACTIVE":

            return jsonify({
                "msg": "Profile đang bị ẩn",
                "slug": slug,
                "trangThai": card["trangThai"]
            }), 403

        # -------------------------------------------------
        # LINKS
        # -------------------------------------------------

        cur.execute("""
            SELECT
                category,
                platform,
                item_type,
                display_title,
                value,
                sort_order
            FROM card_items
            WHERE card_id=%s
              AND is_active=TRUE
            ORDER BY sort_order
        """, (card["id"],))

        card["links"] = cur.fetchall()

        # -------------------------------------------------
        # CERTIFICATES
        # -------------------------------------------------

        cur.execute("""
            SELECT
                tenChungChi,
                donViCap,
                moTa,
                url,
                ngayCap
            FROM card_certificates
            WHERE card_id=%s
              AND is_active=TRUE
            ORDER BY sort_order
        """, (card["id"],))

        card["certificates"] = cur.fetchall()

        # -------------------------------------------------
        # Trả dữ liệu public
        # -------------------------------------------------

        print("PUBLIC CARD OK - ID:", card["id"])

        return jsonify(card)

    except Exception as ex:

        print("========================================")
        print("PUBLIC CARD ERROR:")
        print(ex)
        print("========================================")

        return jsonify({
            "msg": "Không thể tải profile",
            "error": str(ex)
        }), 500

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

# =========================================================
# CARD ITEMS
# =========================================================


@card_bp.get("/api/cards/<int:card_id>/items")
def get_card_items(card_id):

    admin = require_admin()

    if not admin:
        return jsonify({
            "msg": "Không có quyền"
        }), 403

    user_id = admin["id"]

    try:

        # Kiểm tra card có thuộc admin không
        card = get_owned_card(card_id, user_id)

        if not card:
            return jsonify({
                "msg": "Không tìm thấy thẻ"
            }), 404

        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute("""
            SELECT
                id,
                card_id,
                category,
                platform,
                item_type,
                display_title,
                value,
                sort_order,
                is_active
            FROM card_items
            WHERE card_id=%s
              AND is_active=TRUE
            ORDER BY sort_order, id
        """, (card_id,))

        items = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify(items)

    except Exception as ex:

        print("GET CARD ITEMS ERROR:", ex)

        return jsonify({
            "msg": "Không thể lấy card items",
            "error": str(ex)
        }), 500


# =========================================================
# CREATE ITEM
# =========================================================

@card_bp.post("/api/cards/<int:card_id>/items")
def create_card_item(card_id):

    admin = require_admin()

    if not admin:
        return jsonify({
            "msg": "Không có quyền"
        }), 403

    user_id = admin["id"]

    try:

        # Kiểm tra card
        card = get_owned_card(card_id, user_id)

        if not card:
            return jsonify({
                "msg": "Không tìm thấy thẻ"
            }), 404

        data = request.get_json(silent=True) or {}

        category = data.get("category")
        platform = data.get("platform")
        item_type = data.get("item_type")
        display_title = data.get("display_title")
        value = data.get("value")

        if not category:
            return jsonify({
                "msg": "Thiếu category"
            }), 400

        if not item_type:
            return jsonify({
                "msg": "Thiếu item_type"
            }), 400

        if not value:
            return jsonify({
                "msg": "Thiếu giá trị"
            }), 400

        # Lấy sort order cuối cùng
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT COALESCE(MAX(sort_order), 0)
            FROM card_items
            WHERE card_id=%s
        """, (card_id,))

        max_order = cur.fetchone()[0]

        cur.execute("""
            INSERT INTO card_items
            (
                card_id,
                category,
                platform,
                item_type,
                display_title,
                value,
                sort_order,
                is_active
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,TRUE)
        """, (
            card_id,
            category,
            platform,
            item_type,
            display_title,
            value,
            max_order + 1
        ))

        item_id = cur.lastrowid

        conn.commit()

        cur.close()
        conn.close()

        return jsonify({
            "msg": "Thêm item thành công",
            "id": item_id
        }), 201

    except Exception as ex:

        print("CREATE CARD ITEM ERROR:", ex)

        return jsonify({
            "msg": "Không thể thêm item",
            "error": str(ex)
        }), 500


# =========================================================
# UPDATE ITEM
# =========================================================

@card_bp.put("/api/cards/<int:card_id>/items/<int:item_id>")
def update_card_item(card_id, item_id):

    admin = require_admin()

    if not admin:
        return jsonify({
            "msg": "Không có quyền"
        }), 403

    user_id = admin["id"]

    try:

        card = get_owned_card(card_id, user_id)

        if not card:
            return jsonify({
                "msg": "Không tìm thấy thẻ"
            }), 404

        data = request.get_json(silent=True) or {}

        display_title = data.get("display_title")
        value = data.get("value")

        if not display_title:
            return jsonify({
                "msg": "Thiếu tiêu đề"
            }), 400

        if not value:
            return jsonify({
                "msg": "Thiếu giá trị"
            }), 400

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE card_items
            SET
                display_title=%s,
                value=%s
            WHERE id=%s
              AND card_id=%s
        """, (
            display_title,
            value,
            item_id,
            card_id
        ))

        if cur.rowcount == 0:

            conn.rollback()

            cur.close()
            conn.close()

            return jsonify({
                "msg": "Không tìm thấy item"
            }), 404

        conn.commit()

        cur.close()
        conn.close()

        return jsonify({
            "msg": "Cập nhật item thành công"
        })

    except Exception as ex:

        print("UPDATE CARD ITEM ERROR:", ex)

        return jsonify({
            "msg": "Không thể cập nhật item",
            "error": str(ex)
        }), 500


# =========================================================
# DELETE ITEM
# =========================================================

@card_bp.delete("/api/cards/<int:card_id>/items/<int:item_id>")
def delete_card_item(card_id, item_id):

    admin = require_admin()

    if not admin:
        return jsonify({
            "msg": "Không có quyền"
        }), 403

    user_id = admin["id"]

    try:

        card = get_owned_card(card_id, user_id)

        if not card:
            return jsonify({
                "msg": "Không tìm thấy thẻ"
            }), 404

        conn = get_connection()
        cur = conn.cursor()

        # Không xóa vật lý
        cur.execute("""
            UPDATE card_items
            SET is_active=FALSE
            WHERE id=%s
              AND card_id=%s
        """, (
            item_id,
            card_id
        ))

        if cur.rowcount == 0:

            conn.rollback()

            cur.close()
            conn.close()

            return jsonify({
                "msg": "Không tìm thấy item"
            }), 404

        conn.commit()

        cur.close()
        conn.close()

        return jsonify({
            "msg": "Xóa item thành công"
        })

    except Exception as ex:

        print("DELETE CARD ITEM ERROR:", ex)

        return jsonify({
            "msg": "Không thể xóa item",
            "error": str(ex)
        }), 500