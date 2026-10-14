"""Скачивание демонстрационных изображений в локальное хранилище.

Файлы сохраняются под именами, на которые ссылается app/db/seed_demo.sql,
в каталог UPLOAD_DIR (по умолчанию uploads, раздаётся по /media).
Запуск из каталога roommate-backend: python scripts/seed_media.py
"""

import os
import urllib.request
from pathlib import Path

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")

# Имя локального файла -> исходный URL (Pinterest).
MEDIA = {
    '0f9a6f86e2806b20e766fd3ae2897257.jpg': 'https://i.pinimg.com/originals/0f/9a/6f/0f9a6f86e2806b20e766fd3ae2897257.jpg',
    '72beea79877602f2ec1967220986ba04.jpg': 'https://i.pinimg.com/736x/72/be/ea/72beea79877602f2ec1967220986ba04.jpg',
    '3a25d4c633cf0b4b8bb3af3adb91d9a4.jpg': 'https://i.pinimg.com/originals/3a/25/d4/3a25d4c633cf0b4b8bb3af3adb91d9a4.jpg',
    '90dd7cb2ad56954bbaa07d1fddf1fe5e.jpg': 'https://i.pinimg.com/736x/90/dd/7c/90dd7cb2ad56954bbaa07d1fddf1fe5e.jpg',
    '4f0e9319727ef9683e336110a5a05349.jpg': 'https://i.pinimg.com/736x/4f/0e/93/4f0e9319727ef9683e336110a5a05349.jpg',
    '8be902ec9450bc7c19a36456c984d6d2.jpg': 'https://i.pinimg.com/736x/8b/e9/02/8be902ec9450bc7c19a36456c984d6d2.jpg',
    '87e63dae76b36fe3de1f780f3330f54c.jpg': 'https://i.pinimg.com/736x/87/e6/3d/87e63dae76b36fe3de1f780f3330f54c.jpg',
    'c9d25b6d8931b8ede1e06e35f4146c59.jpg': 'https://i.pinimg.com/originals/c9/d2/5b/c9d25b6d8931b8ede1e06e35f4146c59.jpg',
    '33408b603df7e97224129767a3543a46.jpg': 'https://i.pinimg.com/736x/33/40/8b/33408b603df7e97224129767a3543a46.jpg',
    '0102f6b0c194e0dc84f19a69a3871d05.jpg': 'https://i.pinimg.com/736x/01/02/f6/0102f6b0c194e0dc84f19a69a3871d05.jpg',
    '515c50352f4c4c0193185c0a158a9ee0.png': 'https://i.pinimg.com/originals/51/5c/50/515c50352f4c4c0193185c0a158a9ee0.png',
    '2ab19370b02abedfa2c92178b76b0b69.jpg': 'https://i.pinimg.com/originals/2a/b1/93/2ab19370b02abedfa2c92178b76b0b69.jpg',
    'd142d78bba16551bc77e003fb13affb7.jpg': 'https://i.pinimg.com/736x/d1/42/d7/d142d78bba16551bc77e003fb13affb7.jpg',
    '8cb9c6117fbd10c243e0143be64b9c4d.jpg': 'https://i.pinimg.com/originals/8c/b9/c6/8cb9c6117fbd10c243e0143be64b9c4d.jpg',
    'eb26e63c95a7ef285341091cd50cb1d9.jpg': 'https://i.pinimg.com/originals/eb/26/e6/eb26e63c95a7ef285341091cd50cb1d9.jpg',
    'ff7ce3d80bb0247a242316930fc80b08.png': 'https://i.pinimg.com/originals/ff/7c/e3/ff7ce3d80bb0247a242316930fc80b08.png',
    'b7a2b753f806877037c9228ea8ca7166.jpg': 'https://i.pinimg.com/originals/b7/a2/b7/b7a2b753f806877037c9228ea8ca7166.jpg',
    '873ffa39fb93a29309ee7724a56dd016.jpg': 'https://i.pinimg.com/originals/87/3f/fa/873ffa39fb93a29309ee7724a56dd016.jpg',
    'aefda5413c7e3fcb3cf8d52c8ce22818.jpg': 'https://i.pinimg.com/originals/ae/fd/a5/aefda5413c7e3fcb3cf8d52c8ce22818.jpg',
    'c669dd33eae0e259a5917dd0bcb9945a.jpg': 'https://i.pinimg.com/736x/c6/69/dd/c669dd33eae0e259a5917dd0bcb9945a.jpg',
    '25d28a4b2409a998615ccbb3edf3eb23.jpg': 'https://i.pinimg.com/originals/25/d2/8a/25d28a4b2409a998615ccbb3edf3eb23.jpg',
    '97a8dfbdecfdf8198664bb04e9e1a9ce.jpg': 'https://i.pinimg.com/736x/97/a8/df/97a8dfbdecfdf8198664bb04e9e1a9ce.jpg',
    '67dccf9516ae9d9f95a36137ed6fe65e.jpg': 'https://i.pinimg.com/originals/67/dc/cf/67dccf9516ae9d9f95a36137ed6fe65e.jpg',
    '252084d7d23d90f523b37a119183c42c.jpg': 'https://i.pinimg.com/originals/25/20/84/252084d7d23d90f523b37a119183c42c.jpg',
    '50a60e33b616bbbec400438cce85e728.jpg': 'https://i.pinimg.com/originals/50/a6/0e/50a60e33b616bbbec400438cce85e728.jpg',
    'f19d74af9d055f9e9db6a7e6f238b098.jpg': 'https://i.pinimg.com/originals/f1/9d/74/f19d74af9d055f9e9db6a7e6f238b098.jpg',
    '385bf995cc608b035944e97f83fd70d3.jpg': 'https://i.pinimg.com/originals/38/5b/f9/385bf995cc608b035944e97f83fd70d3.jpg',
    '99ee2c59c6af155978d1cacd8707a2e7.jpg': 'https://i.pinimg.com/originals/99/ee/2c/99ee2c59c6af155978d1cacd8707a2e7.jpg',
    '0c5d29a39840937f9af0b5f22b4ad5ca.jpg': 'https://i.pinimg.com/736x/0c/5d/29/0c5d29a39840937f9af0b5f22b4ad5ca.jpg',
    'e8932df7ad975cb9f6635cf02a7aeaf2.jpg': 'https://i.pinimg.com/originals/e8/93/2d/e8932df7ad975cb9f6635cf02a7aeaf2.jpg',
    '7c886d65668582172b786fea30ecb3ae.webp': 'https://i.pinimg.com/originals/7c/88/6d/7c886d65668582172b786fea30ecb3ae.webp',
    'd6a685992619668e216e616646ffd7e2.jpg': 'https://i.pinimg.com/originals/d6/a6/85/d6a685992619668e216e616646ffd7e2.jpg',
    '6797616afc0764001e08637fe32d9ff7.jpg': 'https://i.pinimg.com/originals/67/97/61/6797616afc0764001e08637fe32d9ff7.jpg',
    'a3b1c3320486b2adbe92757d9f3e81fc.jpg': 'https://i.pinimg.com/originals/a3/b1/c3/a3b1c3320486b2adbe92757d9f3e81fc.jpg',
    'af9945163c883eb5e2f6228c6add28e5.jpg': 'https://i.pinimg.com/originals/af/99/45/af9945163c883eb5e2f6228c6add28e5.jpg',
    'e65be2f612cad13251100128eb833226.jpg': 'https://i.pinimg.com/736x/e6/5b/e2/e65be2f612cad13251100128eb833226.jpg',
    '3cd701bf3e7a3a65d5e301be1a500729.jpg': 'https://i.pinimg.com/736x/3c/d7/01/3cd701bf3e7a3a65d5e301be1a500729.jpg',
    'f5491e8550a04d0505c895fbbb85ed56.png': 'https://i.pinimg.com/originals/f5/49/1e/f5491e8550a04d0505c895fbbb85ed56.png',
}


def main() -> None:
    target = Path(UPLOAD_DIR)
    target.mkdir(parents=True, exist_ok=True)
    for name, url in MEDIA.items():
        dest = target / name
        if dest.exists():
            continue
        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(request, timeout=30) as response:
            dest.write_bytes(response.read())
        print("saved", name)


if __name__ == "__main__":
    main()
