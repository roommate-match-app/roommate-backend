"""Экспорт OpenAPI-схемы в файл ``openapi.json``.

Фронтенд использует его для генерации типов и mock-сервера:

    python -m scripts.export_openapi
    npx openapi-typescript openapi.json -o src/api/schema.d.ts
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.main import app  # noqa: E402

OUTPUT = Path("openapi.json")


def main() -> None:
    schema = app.openapi()
    OUTPUT.write_text(
        json.dumps(schema, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"OpenAPI: {len(schema['paths'])} путей записано в {OUTPUT}")


if __name__ == "__main__":
    main()
