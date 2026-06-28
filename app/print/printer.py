from escpos.printer import Usb
from PIL import Image, ImageDraw, ImageFont

from app.config.log import create_logger
from app.util.enums import ReceiptStatus


log = create_logger()


def connect_printer():
    log.info("Conectando a impressora USB")
    global printer
    try:
        printer = Usb(
            idVendor=8401,
            idProduct=28679,
            in_ep=0x82,
            out_ep=0x02
        )
    except Exception as ex:
        log.critical("Erro ao conectar a impressora USB:\n{}".format(ex))
        raise ex
    return


def _create_img(order_id: int) -> Image:
    width = 576
    height = 180
    order_id = "#" + str(order_id)

    img = Image.new("RGB", (width, height), "black")
    draw = ImageDraw.Draw(img)

    font = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        140
    )

    bbox = draw.textbbox((0, 0), order_id, font=font)

    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (width - text_width) // 2
    y = (height - text_height) // 2

    draw.text(
        (x, y),
        order_id,
        fill="white",
        font=font
    )
    return img


def _print_base(order_id: int):
    try:
        printer.set(
            align="left",
            font='b',
            double_width=False,
            double_height=False,
            bold=False,
        )

        printer.text("Festival do Japão")
        printer.ln()
        printer.text("Barraquinha de Fukushima\n")
        printer.ln()
        printer.image(_create_img(order_id))
        printer.ln()
        return
    except Exception as ex:
        log.error("Erro ao imprimir a via de id: {}\n{}".format(
            order_id,
            str(ex))
        )
        return ReceiptStatus.error.value


def print_client_receipt(
    order_id: int,
    payment_method: str,
    total_price: float,
    items: list[dict],
):
    log.info("Imprimindo via do cliente de id: {}".format(order_id))

    if isinstance(_print_base(order_id), ReceiptStatus):
        return ReceiptStatus.error.value

    try:
        printer.set(
            align="left",
            font='b',
            double_width=False,
            double_height=False,
            bold=False,
        )
        txt = "Pagamento via {}: R$ {}".format(
                payment_method.value,
                total_price
            )
        printer.text(txt)
        printer.ln()
        for item in items:
            txt = "{}x - {} R$ {}\n".format(
                item["quantity"],
                item["name"],
                item["unit_price"]
            )
            printer.text(txt)
            for customization in item["customizations"]:
                txt = "   ----{}\n".format(customization)
                printer.text(txt)
        printer.cut()
    except Exception as ex:
        log.error("Erro ao imprimir a via do cliente de id: {}\n{}".format(
            order_id,
            str(ex))
        )
        return ReceiptStatus.error.value
    return ReceiptStatus.printed.value


def print_kitchen_receipt(order_id: int, items: list[dict]):
    log.info("Imprimindo via da cozinha de id: {}".format(order_id))

    if isinstance(_print_base(order_id), ReceiptStatus):
        return ReceiptStatus.error.value
    try:
        printer.set(
            align="left",
            font='b'
        )
        for item in items:
            txt = "{}x - {}\n".format(
                item["quantity"], item["name"]
            )
            printer.text(txt)
            for customization in item["customizations"]:
                txt = "   ----{}\n".format(customization)
                printer.text(txt)
        printer.cut()
    except Exception as ex:
        log.error("Erro ao imprimir a via da cozinha de id: {}\n{}".format(
            order_id,
            str(ex))
        )
        return ReceiptStatus.error.value
    return ReceiptStatus.printed.value
