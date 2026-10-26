import hashlib
import hmac

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import get_settings


class SensitiveDataError(Exception):
    """Indica configuração inválida ou falha ao proteger dado sensível."""


def _fernet() -> Fernet:
    key = get_settings().data_encryption_key.get_secret_value().encode("ascii")
    try:
        return Fernet(key)
    except (ValueError, TypeError) as error:
        raise SensitiveDataError("A chave de criptografia configurada é inválida.") from error


def encrypt_sensitive_value(value: str) -> str:
    return _fernet().encrypt(value.encode("utf-8")).decode("ascii")


def decrypt_sensitive_value(value: str) -> str:
    try:
        return _fernet().decrypt(value.encode("ascii")).decode("utf-8")
    except (InvalidToken, UnicodeDecodeError, ValueError) as error:
        raise SensitiveDataError("Não foi possível descriptografar o dado protegido.") from error


def cpf_fingerprint(value: str) -> str:
    normalized = "".join(character for character in value if character.isdigit())
    key = get_settings().cpf_hash_key.get_secret_value().encode("utf-8")
    return hmac.new(key, normalized.encode("ascii"), hashlib.sha256).hexdigest()
