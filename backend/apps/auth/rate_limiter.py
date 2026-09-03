from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

REGISTER_LIMIT = "5/hour"
LOGIN_LIMIT = "10/hour"
TOKEN_REFRESH_LIMIT = "20/hour"
VOICE_CLONE_LIMIT = "10/hour"
