import pytest
from auth import hash_password, verify_password, create_access_token, decode_access_token, SECRET_KEY
from jose import JWTError

def test_hash_password():
    h = hash_password("secret")
    assert h != "secret"
    assert len(h) > 0

def test_verify_password():
    h = hash_password("secret")
    assert verify_password("secret", h) is True
    assert verify_password("wrong", h) is False

def test_create_access_token():
    token = create_access_token(data={"sub": "alice"})
    assert token.count(".") == 2

def test_decode_access_token():
    token = create_access_token(data={"sub": "alice"})
    payload = decode_access_token(token)
    assert payload["sub"] == "alice"
    assert "exp" in payload

def test_decode_access_token_bad_token():
    with pytest.raises(JWTError):
        decode_access_token("bad.token.here")

def test_decode_access_token_wrong_secret():
    from jose import jwt
    bad_token = jwt.encode({"sub": "alice"}, "wrong-secret", algorithm="HS256")
    with pytest.raises(JWTError):
        decode_access_token(bad_token)