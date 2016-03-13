import pytest

from timesheet.model.user import User


PASSWORD = 'password'


def test_authenticate_password_success():
    user     = User(username='james', password=PASSWORD)
    assert user.authenticate(PASSWORD)


@pytest.mark.xfail(raises=ValueError)
def test_authenticate_password_fail():
    user = User(username='james', password=PASSWORD)
    assert user.authenticate('wrong')


def test_change_password_success():
    new_password = 'NEW'
    user = User(username='james', password=PASSWORD)
    assert user.change_password(PASSWORD, new_password=new_password)

    assert user.authenticate(new_password)


def test_changed_password_failed():
    new_password = 'NEW'
    user = User(username='james', password=PASSWORD)

    with pytest.raises(ValueError):
        user.change_password('wrong', new_password=new_password)

    with pytest.raises(ValueError):
        user.authenticate(new_password)

    assert user.authenticate(PASSWORD)
