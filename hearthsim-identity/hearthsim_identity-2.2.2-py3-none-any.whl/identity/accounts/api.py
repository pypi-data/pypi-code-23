from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework import serializers
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.viewsets import GenericViewSet

from ..api.models import APIKey as LegacyAPIKey
from .models import AccountClaim, AuthToken


class LegacyAPIKeyPermission(BasePermission):
	"""
	Permission check for presence of an API Key header
	http://www.django-rest-framework.org/api-guide/permissions/
	"""

	HEADER_NAME = "X-Api-Key"

	def has_permission(self, request, view):
		header = "HTTP_" + self.HEADER_NAME.replace("-", "_").upper()
		key = request.META.get(header, "")
		if not key:
			return False

		try:
			api_key = LegacyAPIKey.objects.get(api_key=key)
		except (LegacyAPIKey.DoesNotExist, DjangoValidationError):
			return False

		request.api_key = api_key
		return api_key.enabled


class RequireAuthToken(BasePermission):
	def has_permission(self, request, view):
		if request.user and request.user.is_staff:
			return True
		return hasattr(request, "auth_token")


class AuthTokenAuthentication(TokenAuthentication):
	model = AuthToken

	def authenticate(self, request):
		user_token_tuple = super(AuthTokenAuthentication, self).authenticate(request)
		if user_token_tuple is not None:
			request.auth_token = user_token_tuple[1]
		return user_token_tuple

	def authenticate_credentials(self, key):
		model = self.get_model()
		try:
			token = model.objects.get(key=key)
		except (model.DoesNotExist, ValueError):
			raise AuthenticationFailed("Invalid token: %r" % (key))

		if token.user:
			if not token.user.is_active:
				raise AuthenticationFailed("User %r cannot log in." % (token.user))

		return token.user, token


class AccountClaimSerializer(serializers.Serializer):
	url = serializers.ReadOnlyField(source="get_absolute_url")
	full_url = serializers.ReadOnlyField(source="get_full_url")
	created = serializers.ReadOnlyField()


class CreateAccountClaimView(CreateAPIView):
	authentication_classes = (AuthTokenAuthentication, )
	permission_classes = (RequireAuthToken, LegacyAPIKeyPermission)
	queryset = AccountClaim.objects.all()
	serializer_class = AccountClaimSerializer

	def create(self, request):
		if request.auth_token.user and not request.auth_token.user.is_fake:
			raise ValidationError("This token has already been claimed.")
		claim, _ = AccountClaim.objects.get_or_create(
			token=request.auth_token,
			defaults={"api_key": request.api_key}
		)
		serializer = self.get_serializer(claim)
		headers = self.get_success_headers(serializer.data)
		response = Response(serializer.data, status=HTTP_201_CREATED, headers=headers)
		return response


class UserSerializer(serializers.Serializer):
	id = serializers.IntegerField(read_only=True)
	battletag = serializers.SerializerMethodField()
	username = serializers.SerializerMethodField()
	is_premium = serializers.SerializerMethodField()

	def get_battletag(self, instance):
		if "request" in self.context and self.context["request"].user == instance:
			return instance.battletag

	def get_username(self, instance):
		if "request" in self.context and self.context["request"].user == instance:
			return instance.username

	def get_is_premium(self, instance):
		if "request" in self.context and self.context["request"].user == instance:
			return instance.is_premium

	def to_representation(self, instance):
		if instance.is_fake:
			return None
		return super(UserSerializer, self).to_representation(instance)


class AuthTokenSerializer(serializers.HyperlinkedModelSerializer):
	key = serializers.UUIDField(read_only=True)
	user = UserSerializer(read_only=True)
	test_data = serializers.BooleanField(default=False)

	class Meta:
		model = AuthToken
		fields = ("key", "user", "test_data")

	def create(self, data):
		api_key = self.context["request"].api_key
		data["creation_apikey"] = api_key
		ret = super(AuthTokenSerializer, self).create(data)
		# Create a "fake" user to correspond to the AuthToken
		ret.create_fake_user(save=False)
		ret.save()
		return ret


class AuthTokenViewSet(
	CreateModelMixin, UpdateModelMixin, RetrieveModelMixin, GenericViewSet
):
	authentication_classes = (AuthTokenAuthentication, )
	permission_classes = (LegacyAPIKeyPermission, )
	queryset = AuthToken.objects.all()
	serializer_class = AuthTokenSerializer


class UserDetailsView(RetrieveAPIView):
	queryset = get_user_model().objects.all()
	serializer_class = UserSerializer
	authentication_classes = (OAuth2Authentication, )
	permission_classes = (IsAuthenticated, )

	def get_object(self):
		return self.request.user
