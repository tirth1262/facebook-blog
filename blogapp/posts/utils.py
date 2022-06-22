import os
import secrets
from PIL import Image


def save_picture(form_picture, size, path):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join('blogapp/' + f'static/{path}/' + picture_fn)
    output_size = (size, size)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn
