from PIL import Image
import io


def load_image_bytes(data: bytes) -> Image.Image:
    return Image.open(io.BytesIO(data)).convert("RGB")
