import io

from decimal import Decimal
from os import getenv

import brcode
import qrcode
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv

from app.api.models import NewPix
from app.config.log import create_logger


log = create_logger()


def create_pix(pix_info: NewPix) -> str:
    load_dotenv()
    pix = brcode.BRCode(
        key=getenv("CNPJ", ""),
        name=getenv("NOME_EMPRESA", ""),
        city="SAO PAULO",
        amount=Decimal(pix_info.total_price),
        description="Barraquinha de Fukushima, Festival do Japão",
        transaction_id=str(pix_info.order_id)
    )
    log.info(pix)
    return str(pix)


def create_pix_qr_code(pix_info: NewPix):

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(create_pix(pix_info))

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="image/png")
