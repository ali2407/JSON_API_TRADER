"""CRUD operations for API keys"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import base64

from . import models, schemas


def _encrypt_value(value: str) -> str:
    """Simple base64 encoding (NOT secure for production!)"""
    # TODO: Use proper encryption like cryptography.fernet in production
    return base64.b64encode(value.encode()).decode()


def _decrypt_value(encrypted: str) -> str:
    """Simple base64 decoding"""
    return base64.b64decode(encrypted.encode()).decode()


def _mask_key(key: str) -> str:
    """Mask API key to show only first 4 and last 4 characters"""
    if len(key) <= 8:
        return "*" * len(key)
    return f"{key[:4]}...{key[-4:]}"


def create_api_key(db: Session, api_key: schemas.APIKeyCreate) -> models.APIKey:
    """Create a new API key"""
    # If setting as default, unset other defaults
    if api_key.is_default:
        db.query(models.APIKey).update({"is_default": False})

    # Encrypt sensitive data (simple encoding for now)
    db_api_key = models.APIKey(
        name=api_key.name,
        exchange=api_key.exchange,
        api_key=_encrypt_value(api_key.api_key),
        api_secret=_encrypt_value(api_key.api_secret),
        btcc_username=_encrypt_value(api_key.btcc_username) if api_key.btcc_username else None,
        btcc_password=_encrypt_value(api_key.btcc_password) if api_key.btcc_password else None,
        testnet=api_key.testnet,
        is_active=api_key.is_active,
        is_default=api_key.is_default,
        notes=api_key.notes,
    )
    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)
    return db_api_key


def get_api_key(db: Session, api_key_id: int) -> Optional[models.APIKey]:
    """Get API key by ID"""
    return db.query(models.APIKey).filter(models.APIKey.id == api_key_id).first()


def get_api_keys(db: Session, active_only: bool = False) -> List[models.APIKey]:
    """Get all API keys"""
    query = db.query(models.APIKey)
    if active_only:
        query = query.filter(models.APIKey.is_active == True)
    return query.order_by(models.APIKey.created_at.desc()).all()


def get_default_api_key(db: Session) -> Optional[models.APIKey]:
    """Get the default API key"""
    return db.query(models.APIKey).filter(
        models.APIKey.is_default == True,
        models.APIKey.is_active == True
    ).first()


def update_api_key(
    db: Session,
    api_key_id: int,
    api_key_update: schemas.APIKeyUpdate
) -> Optional[models.APIKey]:
    """Update API key"""
    db_api_key = get_api_key(db, api_key_id)
    if not db_api_key:
        return None

    update_data = api_key_update.model_dump(exclude_unset=True)

    # If setting as default, unset other defaults
    if update_data.get("is_default") == True:
        db.query(models.APIKey).filter(models.APIKey.id != api_key_id).update({"is_default": False})

    for key, value in update_data.items():
        setattr(db_api_key, key, value)

    db.commit()
    db.refresh(db_api_key)
    return db_api_key


def delete_api_key(db: Session, api_key_id: int) -> bool:
    """Delete API key"""
    db_api_key = get_api_key(db, api_key_id)
    if not db_api_key:
        return False

    db.delete(db_api_key)
    db.commit()
    return True


def get_decrypted_credentials(db: Session, api_key_id: int) -> Optional[dict]:
    """Get decrypted API credentials for use with exchange"""
    db_api_key = get_api_key(db, api_key_id)
    if not db_api_key or not db_api_key.is_active:
        return None

    # Update last used timestamp
    db_api_key.last_used_at = datetime.utcnow()
    db.commit()

    result = {
        'api_key': _decrypt_value(db_api_key.api_key),
        'api_secret': _decrypt_value(db_api_key.api_secret),
    }

    # Add BTCC credentials if present
    if db_api_key.btcc_username:
        result['btcc_username'] = _decrypt_value(db_api_key.btcc_username)
    if db_api_key.btcc_password:
        result['btcc_password'] = _decrypt_value(db_api_key.btcc_password)

    return result


def api_key_to_response(api_key: models.APIKey) -> schemas.APIKey:
    """Convert DB model to response schema with masked key"""
    decrypted_key = _decrypt_value(api_key.api_key)
    return schemas.APIKey(
        id=api_key.id,
        name=api_key.name,
        exchange=api_key.exchange,
        api_key_preview=_mask_key(decrypted_key),
        testnet=api_key.testnet,
        is_active=api_key.is_active,
        is_default=api_key.is_default,
        created_at=api_key.created_at,
        last_used_at=api_key.last_used_at,
        notes=api_key.notes,
    )
