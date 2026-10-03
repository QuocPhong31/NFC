import cloudinary.uploader


ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp"
}


def upload_image(file, folder, public_id=None):

    if not file:
        raise ValueError("Không có file")


    if file.mimetype not in ALLOWED_IMAGE_TYPES:
        raise ValueError(
            "Chỉ hỗ trợ JPG, PNG hoặc WebP"
        )


    options = {
        "folder": folder,
        "resource_type": "image"
    }


    if public_id:

        options["public_id"] = public_id
        options["overwrite"] = True


    result = cloudinary.uploader.upload(
        file,
        **options
    )


    return {
        "url": result["secure_url"],
        "public_id": result["public_id"]
    }