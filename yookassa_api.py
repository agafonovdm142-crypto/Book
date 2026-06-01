"""
Интеграция с ЮKassa API v3
Создание платежей, проверка статуса, webhook
"""
import os, uuid, requests, json

# ═══════════════════════════════════════════════════════════════
# ⚠️  ВСТАВЬТЕ СВОИ ДАННЫЕ ИЗ ЛИЧНОГО КАБИНЕТА ЮKASSA
#    ЛК → Интеграция → Ключи API
# ═══════════════════════════════════════════════════════════════
YOOKASSA_SHOP_ID = os.environ.get('YOOKASSA_SHOP_ID', '').strip()
YOOKASSA_SECRET_KEY = os.environ.get('YOOKASSA_SECRET_KEY', '').strip()
YOOKASSA_TEST_MODE = os.environ.get('YOOKASSA_TEST_MODE', '').strip().lower() == 'true'
# ⚠️  TEST_MODE=true + боевые ключи = invalid_credentials от ЮKassa

BASE_URL = 'https://api.yookassa.ru/v3/'

# Хранилище платежей (в памяти — для Render free tier)
# В проде: Redis или БД
_payments = {}

def _auth():
    """Basic auth для ЮKassa"""
    return (YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY)

def _headers(idempotence_key=None):
    """Заголовки запроса"""
    if not idempotence_key:
        idempotence_key = str(uuid.uuid4())
    return {
        'Content-Type': 'application/json',
        'Idempotence-Key': idempotence_key,
    }

def create_payment(amount=199, description='Живая Книга — Полный доступ', 
                   return_url=None, metadata=None):
    """
    Создать платёж в ЮKassa.
    Возвращает: {payment_id, confirmation_url, status}
    """
    if YOOKASSA_SHOP_ID == 'ВАШ_SHOP_ID':
        return {'error': 'YOOKASSA_SHOP_ID не настроен'}
    
    payload = {
        'amount': {
            'value': f'{amount:.2f}',
            'currency': 'RUB'
        },
        'capture': True,
        'confirmation': {
            'type': 'redirect',
            'return_url': return_url or 'https://kt7ussahgizfm.kimi.page/success.html'
        },
        'description': description,
        'metadata': metadata or {},
    }
    # test mode только если явно включён
    if YOOKASSA_TEST_MODE:
        payload['test'] = True
    
    try:
        resp = requests.post(
            f'{BASE_URL}payments',
            auth=_auth(),
            headers=_headers(),
            json=payload,
            timeout=30
        )
        resp.raise_for_status()
        data = resp.json()
        
        payment_id = data['id']
        confirmation_url = data['confirmation'].get('confirmation_url', '')
        status = data['status']
        
        # Сохраняем
        _payments[payment_id] = {
            'id': payment_id,
            'status': status,
            'amount': amount,
            'created_at': data.get('created_at', ''),
            'metadata': metadata or {},
            'paid': status == 'succeeded',
        }
        
        return {
            'payment_id': payment_id,
            'confirmation_url': confirmation_url,
            'status': status,
            'paid': False,
        }
        
    except requests.exceptions.HTTPError as e:
        try:
            err = e.response.json()
            return {'error': err.get('description', str(e))}
        except:
            return {'error': str(e)}
    except Exception as e:
        return {'error': str(e)}

def check_payment(payment_id):
    """
    Проверить статус платежа.
    Возвращает: {status, paid}
    """
    if payment_id in _payments:
        cached = _payments[payment_id]
        if cached['paid']:
            return {'status': cached['status'], 'paid': True}
    
    if YOOKASSA_SHOP_ID == 'ВАШ_SHOP_ID':
        return {'error': 'YOOKASSA_SHOP_ID не настроен'}
    
    try:
        resp = requests.get(
            f'{BASE_URL}payments/{payment_id}',
            auth=_auth(),
            timeout=30
        )
        resp.raise_for_status()
        data = resp.json()
        
        status = data['status']
        paid = status == 'succeeded'
        
        _payments[payment_id] = {
            'id': payment_id,
            'status': status,
            'paid': paid,
            'metadata': data.get('metadata', {}),
        }
        
        return {'status': status, 'paid': paid}
        
    except Exception as e:
        return {'error': str(e)}

def handle_webhook(data):
    """
    Обработать webhook от ЮKassa.
    Возвращает True если обработка успешна.
    """
    try:
        event = data.get('event', '')
        payment_obj = data.get('object', {})
        payment_id = payment_obj.get('id', '')
        status = payment_obj.get('status', '')
        paid = status == 'succeeded'
        
        _payments[payment_id] = {
            'id': payment_id,
            'status': status,
            'paid': paid,
            'metadata': payment_obj.get('metadata', {}),
        }
        
        print(f"[YOOKASSA WEBHOOK] {event}: payment={payment_id} status={status}")
        return True
        
    except Exception as e:
        print(f"[YOOKASSA WEBHOOK ERROR] {e}")
        return False

def get_payments():
    """Список всех платежей для синхронизации с orders"""
    return list(_payments.values())
