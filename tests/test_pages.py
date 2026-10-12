import pytest


@pytest.mark.parametrize("path", ["/", "/my_events"])
def test_public_pages_render(client, path):
    response = client.get(path)

    assert response.status_code == 200
    assert response.mimetype == "text/html"


def test_own_profile_renders(client, make_user, login):
    login(make_user("Лев"))

    response = client.get("/profile")

    assert response.status_code == 200
    assert "Лев" in response.text


def test_profile_without_session_renders_error_page(client):
    response = client.get("/profile")

    assert response.status_code == 401
    assert response.mimetype == "text/html"
