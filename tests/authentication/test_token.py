import string
from random import shuffle

import pytest

from timesheet.model.token import Token


@pytest.fixture
def secret():
    return Token.create_secret()


@pytest.fixture
def token(secret):
    return Token(name='Test Token', value=secret)


def test_create_secret_looks_right(secret):
    assert len(secret) == 64
    assert all(char in string.hexdigits for char in secret)


def test_create_secret_differs():
    sample_size = range(10000)
    secrets     = set(Token.create_secret() for i in sample_size)

    assert len(secrets) == len(sample_size)


def test_token_not_stored_plaintext(secret, token):
    assert token._value != secret
    assert token.value  != secret


def test_token_is_stored(token):
    assert token.value
    assert token._value


def test_authenticate_password_success(secret, token):
    assert token.authenticate(secret)


@pytest.mark.xfail(raises=ValueError)
def test_authenticate_password_fail(token):
    assert token.authenticate('wrong')


def test_value_remains_same_after_use(secret, token):
    correct   = [secret] * 100
    incorrect = ['wrong'] * 100
    attempts  = correct + incorrect

    shuffle(attempts)

    def not_changed(value):
        return token.value == value

    for attempt in attempts:
        print('Authenticating with password {}'.format(attempt))
        try:
            token.authenticate(attempt)
        except ValueError:
            pass
        finally:
            assert not_changed(token.value)
