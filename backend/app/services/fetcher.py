from dataclasses import dataclass
import httpx
from app.config import Settings
from app.security import validate_public_url

@dataclass
class FetchedSource:
    url: str; final_url: str; content: bytes; content_type: str

class FetchError(Exception):
    def __init__(self, code: str, message: str, retryable: bool = False):
        super().__init__(message); self.code = code; self.retryable = retryable

async def fetch_source(url: str, settings: Settings) -> FetchedSource:
    validate_public_url(url)
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=settings.fetch_timeout, headers={"User-Agent": settings.user_agent}) as client:
            async with client.stream("GET", url) as response:
                if response.status_code >= 400:
                    raise FetchError("HTTP_ERROR", f"Source returned HTTP {response.status_code}.", response.status_code >= 500)
                content_type = response.headers.get("content-type", "").split(";", 1)[0].lower()
                if content_type not in {"text/html", "application/xhtml+xml", "text/plain", "application/json", "application/xml", "text/xml"}:
                    raise FetchError("UNSUPPORTED_CONTENT_TYPE", f"Unsupported content type: {content_type or 'unknown'}.")
                chunks: list[bytes] = []; total = 0
                async for chunk in response.aiter_bytes():
                    total += len(chunk)
                    if total > settings.max_response_size:
                        raise FetchError("CONTENT_TOO_LARGE", "The response exceeds the configured size limit.")
                    chunks.append(chunk)
                return FetchedSource(url, str(response.url), b"".join(chunks), content_type)
    except httpx.TimeoutException as exc:
        raise FetchError("FETCH_TIMEOUT", "The source website did not respond within the configured timeout.", True) from exc
    except httpx.RequestError as exc:
        raise FetchError("NETWORK_ERROR", "The source could not be reached.", True) from exc
