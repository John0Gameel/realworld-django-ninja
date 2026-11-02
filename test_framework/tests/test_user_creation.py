import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_create_user():
    assert User.objects.count() == 0  # the test DB starts empty

    user = User.objects.create_user(email="me@example.com", username="me", password="secret")

    assert User.objects.count() == 1
    assert User.objects.get(username="me") == user
    assert user.check_password("secret")


@pytest.mark.django_db
def test_db_is_rolled_back_between_tests():
    # the user from the previous test is gone
    assert User.objects.count() == 0
