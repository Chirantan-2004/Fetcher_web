import ipaddress
import socket
from urllib.parse import urlparse
from fastapi import HTTPException

def validate_public_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise HTTPException(422, detail={"code": "INVALID_URL", "message": "Only HTTP(S) URLs with a hostname are supported."})
    host = parsed.hostname
    try:
        addresses = {item[4][0] for item in socket.getaddrinfo(host, None)}
        for address in addresses:
            ip = ipaddress.ip_address(address)
            if not ip.is_global:
                raise HTTPException(422, detail={"code": "BLOCKED_PRIVATE_NETWORK", "message": "Private and local network targets are not allowed."})
    except socket.gaierror as exc:
        raise HTTPException(422, detail={"code": "DNS_ERROR", "message": "The hostname could not be resolved."}) from exc
    return value
