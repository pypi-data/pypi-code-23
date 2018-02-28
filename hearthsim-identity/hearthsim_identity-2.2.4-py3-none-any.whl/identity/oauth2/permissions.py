from rest_framework.permissions import BasePermission, SAFE_METHODS


class BaseOAuth2HasScopes(BasePermission):
	"""
	Permission check that authorizes tokens with a specific scope.
	"""

	READ_SCOPES = None
	WRITE_SCOPES = None
	ALLOW_NON_OAUTH2_AUTHENTICATION = True

	def has_permission(self, request, view) -> bool:
		if not request.user.is_authenticated:
			return False

		token = request.auth
		if not token or not hasattr(token, "scope"):
			return self.ALLOW_NON_OAUTH2_AUTHENTICATION

		if request.method in SAFE_METHODS:
			return token.is_valid(self.READ_SCOPES)
		else:
			return token.is_valid(self.WRITE_SCOPES)


def OAuth2HasScopes(read_scopes, write_scopes):
	return type("OAuth2HasScopes", (BaseOAuth2HasScopes, ), {
		"READ_SCOPES": read_scopes,
		"WRITE_SCOPES": write_scopes,
	})
