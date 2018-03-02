from octo_drf.settings import project_settings
from django.contrib import auth
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import status, views, generics
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.settings import api_settings
from rest_framework.generics import get_object_or_404

from octo_drf.apps.mailer.api import notify_user
from .serializers import PasswordResetSerializer, UserRegisterSerializer
from .serializers import PasswordResetInplaceSerializer, UserLoginSerializer


OctoUser = get_user_model()
auth_settings = project_settings['auth']
error = api_settings.NON_FIELD_ERRORS_KEY


class RegisterView(generics.GenericAPIView):

    serializer_class = UserRegisterSerializer

    def get(self, request):
        if request.user.is_authenticated():
            return Response(auth_settings['register_handler'](request))
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            hash = urlsafe_base64_encode(force_bytes(user.pk))
            url = reverse('register_confirm', kwargs={'uidb64': hash}),
            notify_user(
                'user_registration',
                user.email,
                context={
                    'url': url, 'hash': hash,
                    'id': user.id, 'email': user.email,
                    'request': request
                }
            )
            return Response({'status': 'Проверьте почту для подтверждения регистрации',
                             'url': url
                             })
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class RegisterRepeatView(views.APIView):

    def get(self, request):
        email = request.GET.get('email')
        user = get_object_or_404(OctoUser, email=email)
        if not user.is_active:
            hash = urlsafe_base64_encode(force_bytes(user.pk))
            url = reverse('register_confirm', kwargs={'uidb64': hash}),
            notify_user(
                'user_registration_repeat',
                user.email,
                context={'hash': hash, 'url': url, 'request': request}
            )
            return Response({'status': 'Проверьте почту для подтверждения регистрации',
                             'url': url
                             })
        return Response(status=status.HTTP_400_BAD_REQUEST)


class LoginView(generics.GenericAPIView):

    serializer_class = UserLoginSerializer

    def get(self, request):
        if request.user.is_authenticated():
            return Response(auth_settings['login_handler'](request))
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            auth.login(request, serializer.validated_data)
            return Response(auth_settings['login_handler'](request))
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class LogOutView(views.APIView):

    def get(self, request):
        auth.logout(request)
        return Response(status.HTTP_200_OK)


class RegisterConfirmView(views.APIView):

    def get(self, request, uidb64=None):
        try:
            decode_uidb64 = force_text(urlsafe_base64_decode(uidb64))
            user = OctoUser.objects.get(pk=decode_uidb64)
            user.is_active = True
            user.save(update_fields=['is_active'])
        except (TypeError, ValueError, OctoUser.DoesNotExist):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(auth_settings['register_confirm_handler'](request))


class ResetPasswordRequestView(views.APIView):

    def get(self, request):
        try:
            email = request.GET.get('email')
            user = OctoUser.objects.get(email=email)
        except OctoUser.DoesNotExist:
            return Response({error: ['Пользователя с таким адресом не существует']},
                            status=status.HTTP_404_NOT_FOUND)
        hash = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        url = reverse('password_confirm', kwargs={'uidb64': hash, 'token': token})
        notify_user(
            'user_password_reset',
            email,
            context={'hash': hash, 'token': token, 'url': url, 'request': request}
        )
        return Response({'success': 'Проверьте почту для сброса пароля',
                         'url': url
                         })


class ResetPasswordConfirmView(generics.GenericAPIView):

    serializer_class = PasswordResetSerializer

    def post(self, request, uidb64=None, token=None):
        uidb64 = self.kwargs.get('uidb64')
        token = self.kwargs.get('token')
        try:
            decode_uidb64 = force_text(urlsafe_base64_decode(uidb64))
            user = OctoUser.objects.get(pk=decode_uidb64)
        except (DjangoUnicodeDecodeError, OctoUser.DoesNotExist):
            return Response(status.HTTP_400_BAD_REQUEST)
        if default_token_generator.check_token(user, token):
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user.set_password(serializer.validated_data['password_1'])
            user.save()
            return Response(auth_settings['reset_password_confirm_handler'](request))
        else:
            return Response({error: ['Ссылка не действительна']},
                            status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordInplace(generics.GenericAPIView):

    serializer_class = PasswordResetInplaceSerializer

    def post(self, request):
        user = get_object_or_404(OctoUser, pk=request.user.pk)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user.set_password(serializer.data['new_password_1'])
            user.save()
            return Response(auth_settings['reset_password_inplace_handler'](request))
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
