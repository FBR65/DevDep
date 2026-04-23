from slowapi import Limiter
from limiter import limiter

def test_limiter_instance():
    assert isinstance(limiter, Limiter)