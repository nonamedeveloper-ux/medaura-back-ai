import httpx

# Patch httpx SSL verification before any google-genai import
_orig_client_init = httpx.Client.__init__
_orig_async_init = httpx.AsyncClient.__init__

def _no_verify_init(self, *args, **kwargs):
    kwargs['verify'] = False
    _orig_client_init(self, *args, **kwargs)

def _no_verify_async_init(self, *args, **kwargs):
    kwargs['verify'] = False
    _orig_async_init(self, *args, **kwargs)

httpx.Client.__init__ = _no_verify_init
httpx.AsyncClient.__init__ = _no_verify_async_init

from app.config import settings
from app.main import app

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=settings.PORT,
        debug=settings.ENVIRONMENT == "development",
    )
