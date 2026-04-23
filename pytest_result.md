cd devdep/workspace && uv run python -m pytest tests/ -v

============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.3, pluggy-1.6.0 -- /home/speedy/Dokumente/dev/DevDep/.venv/bin/python3
cachedir: .pytest_cache
rootdir: /home/speedy/Dokumente/dev/DevDep
configfile: pyproject.toml
plugins: asyncio-1.3.0, anyio-4.13.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 37 items

tests/test_auth.py::TestRegister::test_register_success PASSED           [  2%]
tests/test_auth.py::TestRegister::test_register_duplicate_username PASSED [  5%]
tests/test_auth.py::TestRegister::test_register_duplicate_email PASSED   [  8%]
tests/test_auth.py::TestRegister::test_register_invalid_email PASSED     [ 10%]
tests/test_auth.py::TestLogin::test_login_success PASSED                 [ 13%]
tests/test_auth.py::TestLogin::test_login_wrong_password PASSED          [ 16%]
tests/test_auth.py::TestLogin::test_login_nonexistent_user PASSED        [ 18%]
tests/test_auth.py::TestRateLimiting::test_register_rate_limit PASSED    [ 21%]
tests/test_auth.py::TestRateLimiting::test_login_rate_limit PASSED       [ 24%]
tests/test_auth_unit.py::test_hash_password PASSED                       [ 27%]
tests/test_auth_unit.py::test_verify_password PASSED                     [ 29%]
tests/test_auth_unit.py::test_create_access_token PASSED                 [ 32%]
tests/test_auth_unit.py::test_decode_access_token PASSED                 [ 35%]
tests/test_auth_unit.py::test_decode_access_token_bad_token PASSED       [ 37%]
tests/test_auth_unit.py::test_decode_access_token_wrong_secret PASSED    [ 40%]
tests/test_database.py::test_engine_is_sqlite PASSED                     [ 43%]
tests/test_database.py::test_get_session_yields_session PASSED           [ 45%]
tests/test_dependencies.py::test_get_current_user_success PASSED         [ 48%]
tests/test_dependencies.py::test_get_current_user_missing_token PASSED   [ 51%]
tests/test_dependencies.py::test_get_current_user_nonexistent_user PASSED [ 54%]
tests/test_limiter.py::test_limiter_instance PASSED                      [ 56%]
tests/test_models.py::test_user_columns PASSED                           [ 59%]
tests/test_schemas.py::test_user_create_valid PASSED                     [ 62%]
tests/test_schemas.py::test_user_create_invalid_email PASSED             [ 64%]
tests/test_schemas.py::test_user_update_partial PASSED                   [ 67%]
tests/test_schemas.py::test_token PASSED                                 [ 70%]
tests/test_schemas.py::test_user_public_from_attributes PASSED           [ 72%]
tests/test_users.py::TestGetMe::test_get_me_success PASSED               [ 75%]
tests/test_users.py::TestGetMe::test_get_me_no_auth PASSED               [ 78%]
tests/test_users.py::TestUpdateMe::test_update_me_full PASSED            [ 81%]
tests/test_users.py::TestUpdateMe::test_update_me_partial PASSED         [ 83%]
tests/test_users.py::TestGetUser::test_get_user_success PASSED           [ 86%]
tests/test_users.py::TestGetUser::test_get_user_not_found PASSED         [ 89%]
tests/test_users.py::TestListUsers::test_list_users_success PASSED       [ 91%]
tests/test_users.py::TestListUsers::test_list_users_pagination_default PASSED [ 94%]
tests/test_users.py::TestListUsers::test_list_users_pagination_custom PASSED [ 97%]
tests/test_users.py::TestListUsers::test_list_users_limit_max PASSED     [100%]

=============================== warnings summary ===============================
auth.py:11
  /home/speedy/Dokumente/dev/DevDep/devdep/workspace/auth.py:11: UserWarning: SECRET_KEY is using the insecure default. Set a strong SECRET_KEY env var.
    warnings.warn("SECRET_KEY is using the insecure default. Set a strong SECRET_KEY env var.")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================== 37 passed, 1 warning in 10.24s ========================
