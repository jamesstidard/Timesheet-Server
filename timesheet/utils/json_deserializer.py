from multipledispatch import dispatch


@dispatch(type, int)  # noqa
def deserialize(type_, json):
    if type_ is int:
        return json
    elif type_ is str:
        return str(json)
    elif type_ is bool and json == 0:
        return False
    elif type_ is bool and json == 1:
        return True
    else:
        raise ValueError()


@dispatch(type, float)  # noqa
def deserialize(type_, json):
    if type_ is str:
        return str(json)
    if type_ is float:
        return json
    elif type_ is bool and json == 0:
        return False
    elif type_ is bool and json == 1:
        return True
    else:
        raise ValueError()


@dispatch(type, str)  # noqa
def deserialize(type_, json):
    if type_ is int:
        return int(json)
    elif type_ is str:
        return json
    elif type_ is bool and json.lower() in ['false', '0']:
        return False
    elif type_ is bool and json.lower() in ['true', '1']:
        return True
    else:
        raise ValueError()


@dispatch(type, bool)  # noqa
def deserialize(type_, json):
    if type_ is bool:
        return json
    elif type_ is int and json:
        return 1
    elif type_ is int and not json:
        return 0
    else:
        raise ValueError()


@dispatch(type, object)  # noqa
def deserialize(type_, json):
    if json is None:
        return None
    raise ValueError()


@dispatch(type, list)  # noqa
def deserialize(type_, json):
    raise ValueError()
