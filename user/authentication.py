from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailBackend(ModelBackend):
    """
    Custom authentication backend which uses email to authenticate users.
    Inherits from Django's `ModelBackend`.
    Methods:
        authenticate(request, username=None, password=None, **kwargs):
            Attempts to authenticate a user based on email and password.
            Parameters:
                request (HttpRequest): The HTTP request context.
                username (str): The email address of the user attempting to authenticate.
                password (str): The password for the user attempting to authenticate.
            Returns:
                User instance if authentication is successful, None otherwise.
        get_user(user_id):
            Fetches a user based on the user_id.
            Parameters:
                user_id (int): The ID of the user to retrieve.
            Returns:
                User instance if found, None otherwise.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate the user based on email and password.
        If the email and password combination is valid and the user is allowed to authenticate, returns the User object.
        Otherwise, returns None.
        """
        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    def get_user(self, user_id):
        """
        Retrieve a user instance based on user ID.
        If the user exists in the database, returns the User object; otherwise, returns None.
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None