import random
import string
import re
from datetime import datetime


def generate_booking_ref():
    chars = string.ascii_uppercase + string.digits
    return 'EVT-' + ''.join(random.choices(chars, k=8))


def generate_invitation_code():
    return 'INV-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


def slugify(text):
    s = text.lower()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[-\s]+', '-', s)
    return s.strip('-')


def format_currency(amount, symbol='₹'):
    if amount is None:
        return f'{symbol}0'
    return f'{symbol}{amount:,.0f}'


def time_ago(dt):
    now = datetime.utcnow()
    diff = now - dt
    if diff.days > 365:
        return f'{diff.days // 365}y ago'
    elif diff.days > 30:
        return f'{diff.days // 30}mo ago'
    elif diff.days > 0:
        return f'{diff.days}d ago'
    elif diff.seconds > 3600:
        return f'{diff.seconds // 3600}h ago'
    elif diff.seconds > 60:
        return f'{diff.seconds // 60}m ago'
    return 'just now'
