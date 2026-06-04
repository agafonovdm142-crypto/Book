"""
ЮKassa API Integration v2.1
Supabase PostgreSQL support
"""

import os
import json
import hashlib
import uuid
import logging
from datetime import datetime
import requests
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

# === CONFIG ===
SHOP_ID = os.environ.get('YOOKASSA_SHOP_ID', '')
SECRET_KEY = os.environ.get('YOOKASSA_SECRET_KEY', '')
DATABASE_URL = os.environ.get('DATABASE_URL', '')

# === DATABASE ===
def get_db_connection():
    if not DATABASE_URL:
        return None
    try:
        return psycopg2.connect(DATABASE_URL, sslmode='require')
    except Exception as e:
        logger.error(f"DB error: {e}")
        return None

def save_payment(user_id, order_id, amount, status='pending'):
    """Save payment to database"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO payments (user_id, order_id, amount, status, updated_at)
                VALUES (%s, %s, %s, %s, NOW())
                ON CONFLICT (user_id) DO UPDATE SET
                    order_id = EXCLUDED.order_id,
                    amount = EXCLUDED.amount,
                    status = EXCLUDED.status,
                    updated_at = NOW()
            """, (user_id, order_id, amount, status))
            conn.commit()
            return True
    except Exception as e:
        logger.error(f"Save payment error: {e}")
        return False
    finally:
        conn.close()

def create_payment(amount, user_id, description="Живая Книга - доступ к главам 4-7"):
    """Create payment via ЮKassa API"""
    if not SHOP_ID or not SECRET_KEY:
        logger.error("YOOKASSA credentials not configured")
        return None
    
    idempotence_key = str(uuid.uuid4())
    
    headers = {
        'Idempotence-Key': idempotence_key,
        'Content-Type': 'application/json',
    }
    
    auth = (SHOP_ID, SECRET_KEY)
    
    data = {
        "amount": {
            "value": str(amount),
            "currency": "RUB"
        },
        "capture": True,
        "confirmation": {
            "type": "redirect",
            "return_url": "https://kt7ussahgizfm.kimi.page/success.html"
        },
        "description": description,
        "metadata": {
            "user_id": str(user_id)
        }
    }
    
    try:
        response = requests.post(
            'https://api.yookassa.ru/v3/payments',
            json=data,
            headers=headers,
            auth=auth
        )
        response.raise_for_status()
        result = response.json()
        
        # Save pending payment
        save_payment(user_id, result['id'], amount, 'pending')
        
        return {
            'payment_id': result['id'],
            'confirmation_url': result['confirmation']['confirmation_url']
        }
    except Exception as e:
        logger.error(f"Create payment error: {e}")
        return None

def check_payment(payment_id):
    """Check payment status"""
    if not SHOP_ID or not SECRET_KEY:
        return None
    
    try:
        response = requests.get(
            f'https://api.yookassa.ru/v3/payments/{payment_id}',
            auth=(SHOP_ID, SECRET_KEY)
        )
        response.raise_for_status()
        result = response.json()
        
        # Update status in DB
        if result.get('metadata', {}).get('user_id'):
            user_id = int(result['metadata']['user_id'])
            status = result.get('status', 'pending')
            amount = int(float(result['amount']['value']))
            save_payment(user_id, payment_id, amount, status)
        
        return {
            'status': result.get('status'),
            'paid': result.get('paid', False),
            'amount': result.get('amount', {}).get('value')
        }
    except Exception as e:
        logger.error(f"Check payment error: {e}")
        return None

def process_webhook(data):
    """Process webhook from ЮKassa"""
    try:
        payment_id = data.get('object', {}).get('id')
        status = data.get('object', {}).get('status')
        user_id = data.get('object', {}).get('metadata', {}).get('user_id')
        
        if user_id and payment_id:
            user_id = int(user_id)
            amount = int(float(data['object']['amount']['value']))
            save_payment(user_id, payment_id, amount, status)
            logger.info(f"Webhook processed: user={user_id}, status={status}")
            return True
    except Exception as e:
        logger.error(f"Webhook error: {e}")
    
    return False
