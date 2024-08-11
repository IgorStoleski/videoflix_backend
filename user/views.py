from django.shortcuts import redirect, render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from user.serializers import UserSerializer, EmailAuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken, APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import logout, get_user_model
from .tokens import account_activation_token
from django.contrib import messages
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.contrib.auth.tokens import default_token_generator
from django.views.decorators.csrf import csrf_exempt
import json

base_url = 'https://video-flix.de/'
email_url = 'video-flix.de'
User = get_user_model()

def activate(request, uidb64, token):
    """
    Activates a user account based on a UID and a token.
    Attempts to decode the uidb64 to a user's primary key, retrieve the corresponding user object,
    and then check the provided token. If the token is valid and the user exists, it activates
    the user's account by setting `is_active` to True.
    Parameters:
    - request (HttpRequest): The HTTP request object.
    - uidb64 (str): URL-safe base64-encoded ID of the user.
    - token (str): Token for verifying the user's identity.
    Returns:
    - JsonResponse: A JSON response indicating whether the activation was successful or failed,
      with an appropriate HTTP status code. Returns status 200 with a success message if the
      activation is successful, or status 400 with an error message if the activation fails.
    Raises:
    - Does not explicitly raise exceptions but returns a JsonResponse indicating the outcome.
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None
        
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return JsonResponse({'message': 'Account activated successfully. You can now login.'}, status=200)
    else:
        return JsonResponse({'message': 'Activation link is invalid!'}, status=400)


def activate_email(request, user, to_email):
    """
    Sends an account activation email to the specified email address.
    This function constructs an email with both HTML and plain text content for activating a user's account, 
    includes a secure link with a unique token for the user. If the email is sent successfully, it logs a success message; 
    otherwise, it logs an error.
    :param request: The HttpRequest object, used to determine if the request is secure (https).
    :param user: The User model instance representing the user who needs to activate their account.
    :param to_email: The email address to which the activation email will be sent.
    :return: Redirects to the registration page upon execution.
    The email content is rendered using the `activate_account.html` template. It includes details such as the 
    user's username, domain, user ID encoded in URL-safe base64, and an account activation token.    
    It uses 'https' protocol if the request is secure; otherwise, 'http'.
    """
    mail_subject = 'Activate your account'
    html_content = render_to_string("activate_account.html", {
        'user': user.username,
        'domain': email_url,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    text_content = strip_tags(html_content)  # Fallback für E-Mail-Clients, die kein HTML unterstützen
    from_email = 'damigadas@gmail.com'

    msg = EmailMultiAlternatives(mail_subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    if msg.send():
        messages.success(request, f'An email has been sent to {to_email} with a link to activate your account.')
    else:
        messages.error(request, f'Problem sending email to {to_email}, check your email address and try again.')

    return redirect(base_url + 'register/')

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
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_active = False
            user.save()
            activate_email(request, user, user.email)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'success': False, 'message': 'Validation errors', 'errors': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)
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
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = serializer.validated_data['user']
        if not user.is_active:
            return Response({'error': 'Account is not activated.'}, status=status.HTTP_401_UNAUTHORIZED)
        
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


@csrf_exempt
def request_password_reset(request):
    """
    Handles the password reset request for a user.
    Parameters:
    request (HttpRequest): The HTTP request object containing the email for password reset.
    Returns:
    JsonResponse: A JSON response indicating the result of the operation.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    try:
        data = json.loads(request.body.decode('utf-8'))
        email = data.get('email')
        if not email:
            return JsonResponse({'error': 'Email is required'}, status=400)
        
        user = User.objects.get(email=email)
        send_password_reset_email(request, user)
        return JsonResponse({'message': 'Password reset link sent to your email'}, status=200)
    
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({'error': 'Invalid request data'}, status=400)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Invalid email address'}, status=400)

def send_password_reset_email(request, user):
    """
    Sends a password reset email to the user.
    Parameters:
    request (HttpRequest): The HTTP request object.
    user (User): The user object.
    """
    mail_subject = 'Reset your password'
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    reset_link = f"{request.scheme}://{request.get_host()}/password-reset-confirm/{uid}/{token}/"
    
    html_content = render_to_string('password_reset_email.html', {
        'reset_link': reset_link,
        'user': user  
    })
    text_content = strip_tags(html_content)
    
    email = EmailMultiAlternatives(mail_subject, text_content, to=[user.email])
    email.attach_alternative(html_content, "text/html")
    email.send()


@csrf_exempt
def password_reset_confirm(request, uidb64, token):
    """
    Process a password reset request for a user identified by a base64-encoded UID and a token.

    Parameters:
    request (HttpRequest): The HTTP request object containing the method and body.
    uidb64 (str): A base64-encoded string representing the user's ID.
    token (str): A token used to verify the password reset request.

    Returns:
    JsonResponse: A JSON response indicating the result of the operation.
    """
    user = get_user_by_uid(uidb64)
    
    if user and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            return handle_post_request(request, user)
        else:
            return redirect_to_confirm_page(uidb64, token)
    return JsonResponse({'error': 'Invalid link'}, status=400)


def get_user_by_uid(uidb64):
    """
    Retrieve a user by their base64-encoded UID.
    Parameters:
    uidb64 (str): A base64-encoded string representing the user's ID.
    Returns:
    User: The user object if found, otherwise None.
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        return User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return None


def handle_post_request(request, user):
    """
    Handle a POST request to reset the user's password.
    Parameters:
    request (HttpRequest): The HTTP request object containing the body.
    user (User): The user object whose password is to be reset.
    Returns:
    JsonResponse: A JSON response indicating the result of the operation.
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
        new_password = data.get('new_password')
        if new_password:
            user.set_password(new_password)
            user.save()
            return JsonResponse({'message': 'Password has been reset successfully'}, status=200)
        return JsonResponse({'error': 'New password is required'}, status=400)
    except Exception:
        return JsonResponse({'error': 'Invalid request data'}, status=400)


def redirect_to_confirm_page(uidb64, token):
    """
    Redirect to the password reset confirmation page.
    Parameters:
    uidb64 (str): A base64-encoded string representing the user's ID.
    token (str): A token used to verify the password reset request.
    Returns:
    HttpResponseRedirect: A redirect to the password reset confirmation page.
    """
    return redirect(f"{base_url}/password-reset-confirm/{uidb64}/{token}/")