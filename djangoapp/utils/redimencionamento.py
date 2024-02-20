from PIL import Image
from pathlib import Path
from django.conf import settings


def resize_image(image_django, new_width=800, optimize=True, quality=60):
    image_path = Path(settings.MEDIA_ROOT / image_django.name).resolve()
    image_pillow = Image.open(image_path)

    width, height = image_pillow.size
    # exif = pil_image.info['exif']
    # print(pil_image.info)
    if width <= new_width:
        image_pillow.close()
        return image_pillow
    
    new_height = round(new_width * height / width)

    new_image = image_pillow.resize((new_width, new_height), Image.LANCZOS)
    new_image.save(
        image_path,
        optimize=optimize,
        quality=quality
    )

    return new_image
