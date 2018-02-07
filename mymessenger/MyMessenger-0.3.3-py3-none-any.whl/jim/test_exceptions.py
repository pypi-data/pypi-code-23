from .exceptions import WrongParamsError, TooLongError, WrongActionError, WrongDictError, ResponseCodeError


def test_str():
    wrong_dict = {'test': 'test', 'other': 'other'}

    e = WrongParamsError(wrong_dict)
    assert str(e) == "Wrong action params: {'test': 'test', 'other': 'other'}" or \
           str(e) == "Wrong action params: {'other': 'other', 'test': 'test'}"
    e = TooLongError('field_name', 30, 25)
    assert str(e) == "field_name: 30 to long (> 25 symbols)"
    e = WrongActionError('test_action')
    assert str(e) == "Wrong action: test_action"
    e = WrongDictError(wrong_dict)
    assert str(e) == "Wrong input dict: {'test': 'test', 'other': 'other'}" or \
           str(e) == "Wrong input dict: {'other': 'other', 'test': 'test'}"
    e = ResponseCodeError(666)
    assert str(e) == "Wrong response code: 666"
