import email

from django.contrib.auth import get_user_model, authenticate
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from rest_framework import serializers

User = get_user_model()


class RegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, min_length=12, max_length=20)
    password_confirm = serializers.CharField(required=True)
    name = serializers.CharField(required=True, min_length=2, max_length=20)
    last_name = serializers.CharField(required=False, min_length=2, max_length=20)

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('This email was used before')
        return email

    def validate(self, data):
        password = data.get('password')
        password_confirm = data.pop('password_confirm')
        if password != password_confirm:
            raise serializers.ValidationError('Passwords are not identical')
        return data

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.send_activation_email(activation_code=user.code_generator(), email=[User.email])
        return user


class ActivationSerialazer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        code = data.get('code')
        if not User.objects.filter(email=email, activation_code=code).exists():
            raise serializers.ValidationError('User wasn\'t found')
        return data

    def activate(self):
        email = self.validated_data.get('email')
        user = User.objects.get(email=email)
        user.is_active = True
        user.activation_code = ''
        user.save()


class ChangePasswordSerialazer(serializers.Serializer):
    last_password = serializers.CharField(min_length=6, required=True)
    new_password = serializers.CharField(min_length=6, required=True)
    new_password_confirm = serializers.CharField(min_length=6, required=True)

    def validate_last_password(self, password):
        request = self.context.get('request')
        user = request.user
        if not request.user.check_password(password):
            raise serializers.ValidationError('Password is incorrect')
        return password

    def validate(self, attrs):
        last_pass = attrs.get('last_password')
        new_pass1 = attrs.get('new_password')
        new_pass2 = attrs.get('new_password_confirm')
        if new_pass1 != new_pass2:
            raise serializers.ValidationError('Password are not similar')
        elif last_pass == new_pass2:
            raise serializers.ValidationError('Old and new password can NOT be similar')
        return attrs

    def set_new_password(self) -> None:
        '''Menyaet parol u aktivnogo polzovatelya'''
        new_password = self.validated_data.get('new_password')
        user = self.context.get('request').user
        user.set_password(new_password)
        user.save()


class LoginSerialazer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    def validate_email(self, email):
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError('User wasn\'t found')
        return email

    def validate(self, data):
        request = self.context.get('request')
        email = data.get('email')
        password = data.get('password')
        if email and password:
            user = authenticate(username=email, password=password, request=request)
            if not user:
                raise serializers.ValidationError('Invalid password')
        else:
            raise serializers.ValidationError('You have to type you\'re mail and password')
        data['user'] = user
        return data


class ForgotPasswordSerialazer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, email):
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError('User not found')

    def send_verification_mail(self):
        email = self.validated_data.get('email')
        user = User.objects.get(email=email)
        send_mail('Password recovery', f'You\'re verification code is: {user.code_generator()}',
                  'test1@gmail.com', [user.email])


class ForgotPasswordCompleteSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    code = serializers.CharField(required=True)
    password = serializers.CharField(min_length=6, required=True)
    password_confirm = serializers.CharField(min_length=6, required=True)

    def validate(self, attrs):
        email = attrs.get('email')
        code = attrs.get('code')
        password1 = attrs.get('password')
        password2 = attrs.get('password_confirm')

        if not User.objects.filter(email=email, activation_code=code).exists():
            raise serializers.ValidationError('User wasn\'t found')
        if password2 != password1:
            raise serializers.ValidationError('Passwords are not similar')
        return attrs

    def set_new_password(self):
        email = self.validated_data.get('email')
        password = self.validated_data.get('password')
        user = User.objects.get(email=email)
        user.set_password(password)
        user.save()


# class ForgotPassSerializer(serializers.Serializer):
#     email = serializers.EmailField(required=True)
#
#     def validate_email(self, email):
#         if not User.objects.filter(email=email).exists():
#             raise serializers.ValidationError('User not found')

    # def send_verification_mail(self):
    #     email = self.validated_data.get('email')
    #     user = User.objects.get(email=email)
    #     random_password = get_random_string(length=12)
    #     user.set_password(random_password)
    #     send_mail('Password recovery', f'You\'re new password is: {random_password}',
    #               'test1@gmail.com', [user.email])
