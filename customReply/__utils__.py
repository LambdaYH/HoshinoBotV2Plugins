from PIL import ImageFont, ImageDraw
import os
from PIL import Image
import base64
from io import BytesIO

# from https://github.com/Bluefissure/OtterBot/blob/master/ffxivbot/handlers/QQUtils.py#L417
def text2img(text):
    font = ImageFont.truetype(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "resources/fonts/msyh.ttc",
        ),
        20,
    )
    lines = text.split("\n")
    img_height = 0
    img_width = 0
    for line in lines:
        width, height = font.getsize(line)
        img_width = max(img_width, width)
        img_height += height
    border = 10
    img = Image.new(
        "RGB", (img_width + 2 * border, img_height + 2 * border), color="white"
    )
    d = ImageDraw.Draw(img)
    d.text((border, border), text, font=font, fill="#000000")
    output_buffer = BytesIO()
    img.save(output_buffer, format="JPEG")
    byte_data = output_buffer.getvalue()
    base64_str = base64.b64encode(byte_data).decode("utf-8")
    return "base64://" + base64_str