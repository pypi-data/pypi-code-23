from sigauth import permissions

from unittest.mock import patch, Mock


@patch('sigauth.utils.RequestSignatureChecker.test_signature')
def test_signature_has_permission(mock_test_signature):
    permission = permissions.SignatureCheckPermissionBase()
    request = Mock()

    permission.has_permission(request=request, view=Mock())

    mock_test_signature.assert_called_once_with(request)
