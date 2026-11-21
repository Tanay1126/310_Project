import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.repositories import workflow_repository
from app.schemas import Customer


_TOKEN_SECRET = secrets.token_bytes(32)
_TOKEN_TTL_SECONDS = 12 * 60 * 60
_PASSWORD_ITERATIONS = 310_000
_bearer_scheme = HTTPBearer(auto_error=False)


def hash_password(password: str) -> dict[str, str | int]:
    # Use a unique random salt for each password before deriving the hash.
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, _PASSWORD_ITERATIONS
    )
    return {
        "password_salt": base64.urlsafe_b64encode(salt).decode("ascii"),
        "password_hash": base64.urlsafe_b64encode(digest).decode("ascii"),
        "password_iterations": _PASSWORD_ITERATIONS,
    }


def verify_password(password: str, customer: dict[str, Any]) -> bool:
    # Derive the candidate hash with the customer's stored salt and iteration count.
    salt = base64.urlsafe_b64decode(customer["password_salt"])
    expected = base64.urlsafe_b64decode(customer["password_hash"])
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        customer["password_iterations"],
    )
    return hmac.compare_digest(digest, expected)


def create_access_token(customer_id: int, role: str) -> str:
    # Encode a short-lived bearer payload and sign it with the server secret.
    payload = json.dumps(
        {"sub": customer_id, "role": role, "exp": int(time.time()) + _TOKEN_TTL_SECONDS},
        separators=(",", ":"),
    ).encode("utf-8")
    encoded_payload = base64.urlsafe_b64encode(payload).rstrip(b"=").decode("ascii")
    signature = hmac.new(
        _TOKEN_SECRET, encoded_payload.encode("ascii"), hashlib.sha256
    ).digest()
    encoded_signature = base64.urlsafe_b64encode(signature).rstrip(b"=").decode("ascii")
    return f"{encoded_payload}.{encoded_signature}"


def _decode_access_token(token: str) -> dict[str, Any]:
    try:
        # Verify the signature before trusting any claims in the payload.
        encoded_payload, encoded_signature = token.split(".", maxsplit=1)
        signature = base64.urlsafe_b64decode(
            encoded_signature + "=" * (-len(encoded_signature) % 4)
        )
        expected_signature = hmac.new(
            _TOKEN_SECRET, encoded_payload.encode("ascii"), hashlib.sha256
        ).digest()
        if not hmac.compare_digest(signature, expected_signature):
            raise ValueError("Invalid token signature")
        payload = base64.urlsafe_b64decode(
            encoded_payload + "=" * (-len(encoded_payload) % 4)
        )
        claims = json.loads(payload)
        if claims["exp"] <= time.time():
            raise ValueError("Expired token")
        return claims
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error


def get_current_customer(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> Customer:
    # Require a valid customer bearer token and an available matching account.
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    claims = _decode_access_token(credentials.credentials)
    if claims.get("role") != "customer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Customer role required",
        )
    customer = workflow_repository.get_customer(claims["sub"])
    if (
        customer is None
        or not customer["active"]
        or customer["role"] != claims["role"]
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Customer account is unavailable",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Customer.model_validate(customer)
