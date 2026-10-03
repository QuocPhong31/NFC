import cloudinary_config

import qrcode

import cloudinary.uploader

from io import BytesIO


def create_qr(
    url,
    public_id
):

    qr = qrcode.QRCode(

        version=None,

        error_correction=
            qrcode.constants.ERROR_CORRECT_H,

        box_size=10,

        border=4

    )


    qr.add_data(url)

    qr.make(
        fit=True
    )


    img = qr.make_image(

        fill_color="black",

        back_color="white"

    )


    buffer = BytesIO()


    img.save(
        buffer,
        format="PNG"
    )


    buffer.seek(0)


    result = (
        cloudinary
        .uploader
        .upload(

            buffer,

            folder="nfc/qr",

            public_id=public_id,

            overwrite=True,

            resource_type="image"

        )
    )


    return result[
        "secure_url"
    ]