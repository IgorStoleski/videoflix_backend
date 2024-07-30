from datetime import datetime
from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from user.models import CustomUser

User = get_user_model()
class UserSerializer(serializers.ModelSerializer):
    """
    A serializer for user data.
    This serializer handles the serialization and deserialization of User model data.
    It includes fields such as 'id', 'username', 'first_name', 'last_name', 'email', and 'password'.
    The 'password' field is set to write-only to ensure it is not readable or serializable.
    The nested 'Meta' class defines metadata for the serializer:
        - model: Specifies the model to serialize.
        - fields: Defines the fields to include in the serialization.
        - extra_kwargs: Provides additional kwargs for handling field properties, such as making 'password' write-only.
    The 'create' method handles creating a new User instance from validated data:
        - param validated_data: The data that has been validated by the serializer.
        - return: Returns a newly created User instance.
    """
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
    """
    Serializer for email authentication with token generation.
    Attributes:
        email (EmailField): An email field that stores the user's email.
        password (CharField): A write-only password field that stores the user's password.
    Methods:
        validate(data):
            Validates the user's credentials.
            This method checks if the user exists and if the password is correct.
            It also checks if the user's account is active. If any of these checks fail,
            it raises a ValidationError with an appropriate error message.
            Parameters:
                data (dict): A dictionary containing 'email' and 'password' keys.
            Returns:
                dict: A dictionary with a 'user' key containing the user object if authentication is successful.
            Raises:
                ValidationError: An error is raised if the email does not exist, the password is incorrect,
                                 or the account is not active. The specific reason is included in the error message.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        user = authenticate(request=self.context.get('request'), username=email, password=password)        
        if user is None:
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