import os, uuid, requests, json

YOOKASSA_SHOP_ID = os.environ.get('YOOKASSA_SHOP_ID', '').strip()
YOOKASSA_SECRET_KEY = os.environ.get('YOOKASSA_SECRET_KEY', '').strip()
YOOKASSA_TEST_MODE = os.environ.get('YOOKASSA_TEST_MODE', '').strip().lower() == 'true'

BASE_URL = 'https://api.yookassa.ru/v3/'
_payments = {}

def _auth():
    return (YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY)

def _headers():
    return {'Content-Type': 'application/json', 'Idempotence-Key': str(uuid.uuid4())}

def create_payment(amount=199, description='Живая Книга — Полный доступ', return_url=None, metadata=None):
    if not YOOKASSA_SHOP_ID or not YOOKASSA_SECRET_KEY:
        return {'error': 'YOOKASSA credentials not configured'}
    payload = {
        'amount': {'value': f'{amount:.2f}', 'currency': 'RUB'},
        'capture': True,
        'confirmation': {'type': 'redirect', 'return_url': return_url or 'https://kt7ussahgizfm.kimi.page/success.html'},
        'description': description,
        'metadata': metadata or {},
    }
    if YOOKASSA_TEST_MODE:
        payload['test'] = True
    try:
        resp = requests.post(f'{BASE_URL}payments', auth=_auth(), headers=_headers(), json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        _payments[data['id']] = {'id': data['id'], 'status': data['status'], 'paid': False, 'metadata': metadata or {}}
        return {'payment_id': data['id'], 'confirmation_url': data['confirmation'].get('confirmation_url', ''), 'status': data['status'], 'paid': False}
    except Exception as e:
        return {'error': str(e)}

def check_payment(payment_id):
    if payment_id in _payments and _payments[payment_id].get('paid'):
        return {'status': 'succeeded', 'paid': True}
    try:
        resp = requests.get(f'{BASE_URL}payments/{payment_id}', auth=_auth(), timeout=30)
        resp.raise_for_status()
        data = resp.json()
        paid = data['status'] == 'succeeded'
        _payments[payment_id] = {'id': payment_id, 'status': data['status'], 'paid': paid}
        return {'status': data['status'], 'paid': paid}
    except Exception as e:
        return {'error': str(e)}

def handle_webhook(data):
    try:
        obj = data.get('object', {})
        pid = obj.get('id', '')
        status = obj.get('status', '')
        paid = status == 'succeeded'
        _payments[pid] = {'id': pid, 'status': status, 'paid': paid}
        return True
    except:
        return False
      Fix YooKassa credentials
