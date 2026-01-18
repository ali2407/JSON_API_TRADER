"""API Key management endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import sys
import os

# Add parent directory to path to import src modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from .. import schemas
from ..database import get_db
from ..crud_apikeys import (
    create_api_key,
    get_api_key,
    get_api_keys,
    get_default_api_key,
    update_api_key,
    delete_api_key,
    api_key_to_response,
)

router = APIRouter(prefix="/api/keys", tags=["api-keys"])


@router.post("/validate", response_model=schemas.APIKeyValidateResponse)
async def validate_api_key(credentials: schemas.APIKeyValidate):
    """
    Validate API key credentials against the specified exchange.
    Tests the connection and returns account balance if successful.
    """
    exchange = credentials.exchange or "bingx"

    try:
        if exchange == "btcc":
            from src.btcc_client import BTCCClient

            # BTCC requires username/password for authentication
            if not credentials.btcc_username or not credentials.btcc_password:
                return schemas.APIKeyValidateResponse(
                    valid=False,
                    message="BTCC requires username and password for authentication",
                    balance=None,
                    account_type=None
                )

            client = BTCCClient(
                api_key=credentials.api_key,
                api_secret=credentials.api_secret,
                testnet=credentials.testnet
            )

            # Login first to get auth token
            await client.login(credentials.btcc_username, credentials.btcc_password)
            await client.initialize()
            balance = await client.get_balance()

            # Extract balance for BTCC
            usdt_balance = 0.0
            if isinstance(balance, dict):
                usdt_balance = float(balance.get('balance', balance.get('equity', 0)))

            await client.close()

        else:  # Default to BingX
            from src.bingx_client import BingXClient

            client = BingXClient(
                api_key=credentials.api_key,
                api_secret=credentials.api_secret,
                testnet=credentials.testnet
            )
            await client.initialize()
            balance = await client.get_balance()

            # Extract USDT balance for BingX
            usdt_balance = 0.0
            if 'USDT' in balance:
                usdt_balance = float(balance['USDT'].get('free', 0))
            elif 'total' in balance and 'USDT' in balance['total']:
                usdt_balance = float(balance['total']['USDT'])

        return schemas.APIKeyValidateResponse(
            valid=True,
            message="API key validated successfully",
            balance=usdt_balance,
            account_type="testnet" if credentials.testnet else "live"
        )

    except Exception as e:
        error_msg = str(e)
        # Parse common error messages
        if "Invalid API-key" in error_msg or "invalid api" in error_msg.lower():
            error_msg = "Invalid API key"
        elif "Signature" in error_msg or "signature" in error_msg.lower():
            error_msg = "Invalid API secret"
        elif "IP" in error_msg:
            error_msg = "IP address not whitelisted"
        elif "API KEY NOT TRADE AUTH" in error_msg:
            error_msg = (
                "API key lacks trading authorization. "
                "This API uses BTCC 'Futures' endpoints (not 'Futures Pro'). "
                "Please create an API key with 'Futures - Read' and ensure 'Futures - Trade' permissions are enabled."
            )
        elif "permission" in error_msg.lower():
            error_msg = "API key lacks required permissions"

        return schemas.APIKeyValidateResponse(
            valid=False,
            message=f"Validation failed: {error_msg}",
            balance=None,
            account_type=None
        )


@router.post("", response_model=schemas.APIKey, status_code=201)
def add_api_key(api_key: schemas.APIKeyCreate, db: Session = Depends(get_db)):
    """Add a new API key"""
    db_api_key = create_api_key(db=db, api_key=api_key)
    return api_key_to_response(db_api_key)


@router.get("", response_model=List[schemas.APIKey])
def list_api_keys(active_only: bool = False, db: Session = Depends(get_db)):
    """Get all API keys"""
    db_api_keys = get_api_keys(db=db, active_only=active_only)
    return [api_key_to_response(key) for key in db_api_keys]


@router.get("/default", response_model=schemas.APIKey)
def get_default_key(db: Session = Depends(get_db)):
    """Get the default API key"""
    db_api_key = get_default_api_key(db=db)
    if not db_api_key:
        raise HTTPException(status_code=404, detail="No default API key found")
    return api_key_to_response(db_api_key)


@router.get("/{key_id}", response_model=schemas.APIKey)
def get_key(key_id: int, db: Session = Depends(get_db)):
    """Get a specific API key"""
    db_api_key = get_api_key(db=db, api_key_id=key_id)
    if not db_api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    return api_key_to_response(db_api_key)


@router.patch("/{key_id}", response_model=schemas.APIKey)
def update_key(
    key_id: int,
    api_key_update: schemas.APIKeyUpdate,
    db: Session = Depends(get_db)
):
    """Update an API key"""
    db_api_key = update_api_key(db=db, api_key_id=key_id, api_key_update=api_key_update)
    if not db_api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    return api_key_to_response(db_api_key)


@router.delete("/{key_id}", status_code=204)
def remove_api_key(key_id: int, db: Session = Depends(get_db)):
    """Delete an API key"""
    success = delete_api_key(db=db, api_key_id=key_id)
    if not success:
        raise HTTPException(status_code=404, detail="API key not found")
    return None
