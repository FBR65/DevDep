class TestRegister:
    def test_register_success(self, client):
        response = client.post("/register", json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "secret123",
            "full_name": "Alice Wonderland",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "alice"
        assert data["email"] == "alice@example.com"
        assert "hashed_password" not in data
        assert "password" not in data

    def test_register_duplicate_username(self, client, create_user):
        create_user("alice", "alice@example.com", "secret123")
        response = client.post("/register", json={
            "username": "alice",
            "email": "alice2@example.com",
            "password": "secret123",
            "full_name": "Alice 2",
        })
        assert response.status_code == 409
        assert "Username" in response.json()["detail"]

    def test_register_duplicate_email(self, client, create_user):
        create_user("alice", "alice@example.com", "secret123")
        response = client.post("/register", json={
            "username": "alice2",
            "email": "alice@example.com",
            "password": "secret123",
            "full_name": "Alice 2",
        })
        assert response.status_code == 409
        assert "Email" in response.json()["detail"]

    def test_register_invalid_email(self, client):
        response = client.post("/register", json={
            "username": "alice",
            "email": "not-an-email",
            "password": "secret123",
            "full_name": "Alice",
        })
        assert response.status_code == 422


class TestLogin:
    def test_login_success(self, client, create_user):
        create_user("alice", "alice@example.com", "secret123")
        response = client.post("/login", data={
            "username": "alice",
            "password": "secret123",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, create_user):
        create_user("alice", "alice@example.com", "secret123")
        response = client.post("/login", data={
            "username": "alice",
            "password": "wrongpassword",
        })
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        response = client.post("/login", data={
            "username": "nobody",
            "password": "secret123",
        })
        assert response.status_code == 401


class TestRateLimiting:
    def test_register_rate_limit(self, client):
        for i in range(6):
            response = client.post("/register", json={
                "username": f"rateuser{i}",
                "email": f"rate{i}@example.com",
                "password": "secret123",
                "full_name": f"Rate User {i}",
            })
        assert response.status_code == 429

    def test_login_rate_limit(self, client):
        for i in range(6):
            response = client.post("/login", data={
                "username": f"rateuser{i}",
                "password": "secret123",
            })
        assert response.status_code == 429
