from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from user.serializers import UserSerializer, EmailAuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken, APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import logout, get_user_model

User = get_user_model()

# Create your views here.
class UserView(APIView):
    """
    View for creating and retrieving User instances.

    Provides two HTTP methods:
    - POST: To create a new user instance.
    - GET: To retrieve one or all user instances.
    """
    def post(self, request):
        """
        Creates a new user instance.
        Args:
            request (HttpRequest): The request object containing the user data.

        Returns:
            Response: A Django Rest Framework response object with the created user data and HTTP 201 Created status on success.
            If the data is invalid, returns a response with error details and HTTP 400 Bad Request status.
        """
        """ serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) """
        print("Incoming request data:", request.data)  # Debug-Log
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print("Serializer errors:", serializer.errors)  # Debug-Log
        return Response({'success': False, 'message': 'Validation errors', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, pk=None, format=None):
        """
        Retrieves user instance(s).
        Args:
            request (HttpRequest): The request object.
            pk (int, optional): The primary key of the user to retrieve. Defaults to None.
            format (str, optional): The format of the response (e.g., 'json'). Defaults to None.

        Returns:
            Response: A Django Rest Framework response object containing the user data.
            If a specific user is requested and not found, raises NotFound with a 404 status.
        """
        if pk:
            try:
                user = User.objects.get(pk=pk)
                serializer = UserSerializer(user)
            except User.DoesNotExist:
                raise NotFound(detail="User not found", code=404)
        else:
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    

class LoginView(ObtainAuthToken):
    """
    View for handling user authentication requests by verifying email and password,
    and returning an authentication token.
    
    Attributes:
        serializer_class (serializer instance): Specifies the serializer used for
        validating and deserializing input data. It handles email-based authentication.
    """
    serializer_class = EmailAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to authenticate a user.        
        Processes the incoming data through the defined serializer to validate user credentials.
        If credentials are valid, an authentication token is either retrieved or created for
        the user, and the token along with user details are returned.
        Args:
            request (HttpRequest): The request object containing all the data sent with the POST request.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        Returns:
            Response: A response object containing the authentication token, user's ID, and email address
            if the authentication is successful. If credentials are invalid, raises an exception with
            appropriate error messages.        
        Raises:
            ValidationError: An error indicating what went wrong during user validation.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })
        

class LogoutView(APIView):
    """
    A view that handles log out operations for authenticated users.
    This view handles POST requests to log out a user by clearing their session and
    returning an HTTP 204 No Content status, indicating that the server successfully
    processed the request, but is not returning any content.
    Methods:
        post(request): Handles the POST request to log out a user.
    """
    def post(self, request):
        """
        Handle the POST request to log out a user.
        This method logs out the user by calling the `logout` function, which clears
        the user's session. After the user is logged out, the method returns an empty
        response with a 204 No Content status.
        Parameters:
            request (HttpRequest): The request object containing all the details of the request.
        Returns:
            Response: An HTTP Response object with status 204 No Content.
        """
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)