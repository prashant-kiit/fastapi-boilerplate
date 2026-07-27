from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, storage_uri="redis://localhost:6379")

# Rate limiting sets a hard cap that rejects extra calls, while throttling delays or queues those calls to handle traffic surges smoothly
