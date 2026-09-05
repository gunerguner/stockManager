"""pytest-django 基建：用户与 API client fixture。"""
import pytest
from django.contrib.auth.models import User


@pytest.fixture
def user(db) -> User:
    return User.objects.create_user(username="tester", password="pass1234")


@pytest.fixture
def staff_user(db) -> User:
    return User.objects.create_user(
        username="staffer", password="pass1234", is_staff=True
    )


@pytest.fixture
def admin_user(db) -> User:
    return User.objects.create_superuser(username="superadmin", password="pass1234")


@pytest.fixture
def api_client():
    from django.test import Client

    return Client()


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_login(user)
    return api_client
