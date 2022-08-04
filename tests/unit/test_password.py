from app.service.password import Password


def test_password_not_match():
    password = Password("a")
    is_password_ok = password.compare("B")
    assert is_password_ok == "Password and password confirmation not match"


def test_password_without_lowercase():
    password = Password("A")
    is_password_ok = password.compare("A")
    assert is_password_ok == "Password must contain a lowercase letter."
