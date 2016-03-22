import pytest
from random import shuffle

from timesheet.model.user import User


PASSWORD = 'password'


@pytest.fixture
def user():
    return User(username='james', password=PASSWORD)


def test_authenticate_password_success(user):
    assert user.authenticate(PASSWORD)


@pytest.mark.xfail(raises=ValueError)
def test_authenticate_password_fail(user):
    assert user.authenticate('wrong')


def test_change_password_success(user):
    new_password = 'NEW'

    assert user.change_password(PASSWORD, new_password=new_password)
    assert user.authenticate(new_password)


def test_changed_password_failed(user):
    new_password = 'NEW'

    with pytest.raises(ValueError):
        user.change_password('wrong', new_password=new_password)

    with pytest.raises(ValueError):
        user.authenticate(new_password)

    assert user.authenticate(PASSWORD)


def test_password_stored(user):
    assert user._password
    assert user.password


def test_password_not_stored_plaintext(user):
    assert user._password != PASSWORD
    assert user.password != PASSWORD


def test_value_remains_same_after_use(user):
    correct   = [PASSWORD] * 10
    incorrect = ['wrong'] * 10
    attempts  = correct + incorrect

    shuffle(attempts)

    initial = user.password

    for attempt in attempts:
        print('Authenticating with password {}'.format(attempt))
        try:
            user.authenticate(attempt)
        except ValueError:
            pass
        finally:
            assert user.password == initial
