from PIL import Image, ImageDraw, ImageFont
from pathlib import Path


class ImageGenerator:
    def __init__(self, diff: dict):
        self.diff = diff
        self.diff_len = len(diff)
        self.__image_height = max(100, self.diff_len * 20 + 20)
        self.__image_width = 400

        self._image = Image.new(
            "RGB", (self.__image_width, self.__image_height), "white"
        )
        self._draw = ImageDraw.Draw(self._image)
        self._font = ImageFont.load_default()

    def generate_image(self):
        y_text = 10
        for name, (old_status, new_status) in self.diff.items():
            line = f"{name}: {'在线' if old_status == 'online' else '离线'} -> {'在线' if new_status == 'online' else '离线'}"
            self._draw.text((10, y_text), line, font=self._font, fill="black")
            y_text += 20

    def save_image(self, path: Path = Path("frp_status_changes.png")) -> Path:
        self._image.save(path)
        return path
