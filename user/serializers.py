from datetime import datetime
from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from user.models import CustomUser

User = get_user_model()
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data.get('username', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
    
class EmailAuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        # Authenticate user using email and password
        user = authenticate(request=self.context.get('request'), username=email, password=password)
        
        # Debugging: Log authentication attempts
        if user is None:
            # Check if user exists and password matches
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                user_instance = User.objects.get(email=email)
                if not user_instance.check_password(password):
                    raise serializers.ValidationError({'non_field_errors': ['Password is incorrect.']})
                if not user_instance.is_active:
                    raise serializers.ValidationError({'non_field_errors': ['User account is not active.']})
            except User.DoesNotExist:
                raise serializers.ValidationError({'non_field_errors': ['User does not exist.']})

            raise serializers.ValidationError({'non_field_errors': ['Unable to log in with provided credentials.']})
        
        return {'user': user}