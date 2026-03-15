from __future__ import annotations

from pathlib import Path
from typing import Any

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def _load_credentials(client_secrets_file: Path, token_file: Path) -> Credentials:
    creds = None
    if token_file.exists():
        creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(client_secrets_file), SCOPES)
            creds = flow.run_local_server(port=0)
        token_file.write_text(creds.to_json())

    return creds


def upload_to_youtube(
    client_secrets_file: Path,
    token_file: Path,
    video_path: Path,
    title: str,
    description: str,
    tags: list[str],
    privacy_status: str = "private",
) -> dict[str, Any]:
    creds = _load_credentials(client_secrets_file, token_file)
    youtube = build("youtube", "v3", credentials=creds)

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "22",
        },
        "status": {
            "privacyStatus": privacy_status,
        },
    }

    request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload(str(video_path), chunksize=-1, resumable=True),
    )

    response = None
    try:
        while response is None:
            status, response = request.next_chunk()
            if status:
                pass
    except HttpError as exc:
        raise RuntimeError(f"YouTube upload failed: {exc}") from exc

    return response