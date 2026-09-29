
import re
from io import BytesIO

import pytesseract
from PIL import Image

# Ambil username dari 2 kemungkinan pola:
# 1. "t.me/<username>"                -> screenshot Telegram biasa (share/copy link)
# 2. "/<username>" berdiri sendiri     -> screenshot panel "Channel Link" Telegram X,
#    yang cuma nulis "/chanhelle" tanpa prefix "t.me/"
#
# (?<!\S) di alternatif kedua memastikan "/" itu di awal baris/token (bukan bagian
# dari "t.me/" yang sudah ketangkep alternatif pertama, dan bukan pecahan angka
# semacam "11/59").
USERNAME_PATTERN = re.compile(
    r"(?:t\.me/|(?<!\S)/)([A-Za-z][A-Za-z0-9_]{4,31})",
    re.IGNORECASE,
)


def extract_usernames_from_image(image_bytes: bytes) -> list[str]:
    """Baca semua teks di gambar pakai Tesseract (OCR lokal, gratis, tanpa API),
    ambil yang berpola 't.me/<username>' atau '/<username>' (format panel Channel Link).

    Ini fungsi sinkron/blocking, jadi dipanggil lewat asyncio.to_thread()
    di sisi bot supaya tidak ngeblok event loop Telegram.
    """
    image = Image.open(BytesIO(image_bytes))

    # Convert ke grayscale membantu akurasi Tesseract di kebanyakan screenshot
    image = image.convert("L")

    full_text = pytesseract.image_to_string(image)
    found = USERNAME_PATTERN.findall(full_text)

    # Hilangkan duplikat, urutan tetap dipertahankan
    seen = set()
    usernames = []
    for u in found:
        key = u.lower()
        if key not in seen:
            seen.add(key)
            usernames.append(u)
    return usernames
