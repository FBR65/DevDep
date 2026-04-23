from auth import create_access_token


class TestGetMe:
    def test_get_me_success(self, client, create_user):
        create_user("alice", "alice@example.com", "secret123")
        token = create_access_token(data={"sub": "alice"})
        response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "alice"
        assert data["email"] == "alice@example.com"
        assert data["is_active"] is True
        assert "updated_at" in data

    def test_get_me_no_auth(self, client):
        response = client.get("/users/me")
        assert response.status_code == 401


class TestUpdateMe:
    def test_update_me_full(self, client, create_user):
        create_user("alice", "alice@example.com", "secret123")
        token = create_access_token(data={"sub": "alice"})
        response = client.put("/users/me", json={
            "full_name": "Alice Updated",
            "email": "alice_new@example.com",
            "bio": "New bio",
        }, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Alice Updated"
        assert data["email"] == "alice_new@example.com"
        assert data["bio"] == "New bio"

    def test_update_me_partial(self, client, create_user):
        create_user("alice", "alice@example.com", "secret123")
        token = create_access_token(data={"sub": "alice"})
        response = client.put("/users/me", json={
            "bio": "Partial update",
        }, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["bio"] == "Partial update"
        assert data["full_name"] == "Test User"
        assert data["email"] == "alice@example.com"


class TestGetUser:
    def test_get_user_success(self, client, create_user):
        user = create_user("alice", "alice@example.com", "secret123")
        response = client.get(f"/users/{user.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "alice"
        assert "email" not in data
        assert "created_at" not in data

    def test_get_user_not_found(self, client):
        response = client.get("/users/99999")
        assert response.status_code == 404


class TestListUsers:
    def test_list_users_success(self, client, create_user):
        create_user("alice", "alice@example.com", "secret123")
        create_user("bob", "bob@example.com", "secret123")
        response = client.get("/users")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2

    def test_list_users_pagination_default(self, client, create_user):
        for i in range(25):
            create_user(f"user{i}", f"user{i}@example.com", "secret123")
        response = client.get("/users")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 20

    def test_list_users_pagination_custom(self, client, create_user):
        for i in range(5):
            create_user(f"user{i}", f"user{i}@example.com", "secret123")
        response = client.get("/users?offset=2&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_list_users_limit_max(self, client):
        response = client.get("/users?limit=200")
        assert response.status_code == 422
