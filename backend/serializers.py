from datetime import datetime
from django.contrib.auth.models import User 
from django.contrib.auth import authenticate
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating User instances.
    This serializer is responsible for serializing/deserializing User instances
    for use in Django REST Framework views. It includes fields for 'id', 'username',
    'last_name', 'email', and 'password'.
    Attributes:
        model: The User model class to serialize/deserialize.
        fields: The fields to include in the serialization process.
        extra_kwargs: Extra keyword arguments for customizing field behavior.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        """
        Create a new User instance.
        Args:
            validated_data: A dictionary containing validated data for creating a User.
        Returns:
            User: The newly created User instance.
        Raises:
            KeyError: If any required field is missing in the validated data.
        """
        user = User.objects.create_user(
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
    
class EmailAuthTokenSerializer(serializers.Serializer):
    """
    Serializer for authenticating users via email and password.
    Attributes:
        email (serializers.EmailField): The email address of the user.
        password (serializers.CharField): The password of the user.
    Methods:
        validate(self, data): Validates the provided email and password against the user database.
    """
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        """
        Validates the provided email and password against the user database.
        Args:
            data (dict): A dictionary containing 'email' and 'password' keys.
        Returns:
            dict: A dictionary containing a 'user' key if authentication is successful.
        Raises:
            serializers.ValidationError: If provided credentials are invalid.
        """
        user = User.objects.filter(email=data['email']).first()
        if not user:
            raise serializers.ValidationError({'non_field_errors': ['User does not exist.']})
        
        user = authenticate(username=user.username, password=data['password'])
        if not user:
            raise serializers.ValidationError({'non_field_errors': ['Unable to log in with provided credentials.']})

        return {'user': user}