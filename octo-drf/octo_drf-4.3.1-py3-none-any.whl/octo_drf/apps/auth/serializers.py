from django.contrib import auth
from django.contrib.auth import get_user_model
from rest_framework import serializers


OctoUser = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = OctoUser
        fields = ('email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = OctoUser(email=validated_data['email'])
        user.set_password(validated_data['password'])
        user.save()
        return user


class PasswordResetSerializer(serializers.Serializer):

    password_1 = serializers.CharField()
    password_2 = serializers.CharField()

    def validate(self, data):
        password_1 = data.get('password_1')
        password_2 = data.get('password_2')
        if password_1 != password_2:
            raise serializers.ValidationError('Пароли не совпадают!')
        return data


class PasswordResetInplaceSerializer(serializers.Serializer):

    old_password = serializers.CharField()
    new_password_1 = serializers.CharField()
    new_password_2 = serializers.CharField()

    def validate(self, data):
        old_pass = data.get('old_password')
        pass_one = data.get('new_password_1')
        pass_two = data.get('new_password_2')
        user = self.context['request'].user
        if not user.check_password(old_pass):
            raise serializers.ValidationError('Старый пароль введен неверно')
        if pass_one != pass_two:
            raise serializers.ValidationError('Введенные пароли не совпадают')
        return data


class UserLoginSerializer(serializers.Serializer):

    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        user = auth.authenticate(username=email, password=password)
        if user:
            if user.is_active:
                data = user
            else:
                raise serializers.ValidationError('Вы должны подтвердить регистрацию')
        else:
            raise serializers.ValidationError('Вы ввели неверные данные')
        return data
