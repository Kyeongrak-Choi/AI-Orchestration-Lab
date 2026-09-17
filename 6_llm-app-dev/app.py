from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
SAMPLE_HTML = BASE_DIR / "notebooks" / "html" / "sample.html"


async def app(scope, receive, send):
    """스크래핑 연습용 sample.html을 제공하는 간단한 ASGI 앱입니다."""
    if scope["type"] != "http":
        return

    path = scope["path"]

    if path in {"/", "/sample.html"}:
        body = SAMPLE_HTML.read_bytes()
        status = 200
        content_type = "text/html; charset=utf-8"
    elif path == "/health":
        body = b"ok"
        status = 200
        content_type = "text/plain; charset=utf-8"
    else:
        body = b"Not Found"
        status = 404
        content_type = "text/plain; charset=utf-8"

    headers = [
        (b"content-type", content_type.encode("ascii")),
        (b"content-length", str(len(body)).encode("ascii")),
    ]

    await send({"type": "http.response.start", "status": status, "headers": headers})
    await send({"type": "http.response.body", "body": body})
