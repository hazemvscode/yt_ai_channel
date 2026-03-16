from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from ai_video.config import get_config
from ai_video.youtube_upload import _load_credentials


def main() -> None:
    cfg = get_config()
    if not cfg.youtube_client_secrets_file or not cfg.youtube_token_file:
        raise ValueError("Set YOUTUBE_CLIENT_SECRETS_FILE and YOUTUBE_TOKEN_FILE in .env")

    client_secrets = Path(cfg.youtube_client_secrets_file)
    token_file = Path(cfg.youtube_token_file)

    _load_credentials(client_secrets, token_file)
    print(f"Token saved to: {token_file.resolve()}")


if __name__ == "__main__":
    main()
