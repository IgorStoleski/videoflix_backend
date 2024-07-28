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

base_url = 'http://localhost:4200/'
email_url = 'localhost:4200'
User = get_user_model()

def activate(request, uidb64, token):
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
        """ serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) """
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
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            email = data.get('email')
            print(f"Received email: {email}")  # Debugging-Ausgabe
        except Exception as e:
            print(f"Error parsing request body: {e}")  # Debugging-Ausgabe
            return JsonResponse({'error': 'Invalid request data'}, status=400)

        if not email:
            return JsonResponse({'error': 'Email is required'}, status=400)

        try:
            user = User.objects.get(email=email)
            print(f"User found: {user}")  # Debugging-Ausgabe
        except User.DoesNotExist:
            print("User does not exist")  # Debugging-Ausgabe
            return JsonResponse({'error': 'Invalid email address'}, status=400)

        mail_subject = 'Reset your password'
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_link = f"{request.scheme}://{request.get_host()}/password-reset-confirm/{uid}/{token}/"

        html_content = render_to_string('password_reset_email.html', {'reset_link': reset_link})
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(mail_subject, text_content, to=[user.email])
        email.attach_alternative(html_content, "text/html")
        email.send()

        return JsonResponse({'message': 'Password reset link sent to your email'}, status=200)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


@csrf_exempt
def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            try:
                data = json.loads(request.body.decode('utf-8'))
                new_password = data.get('new_password')
                if new_password:
                    user.set_password(new_password)
                    user.save()
                    return JsonResponse({'message': 'Password has been reset successfully'}, status=200)
                else:
                    return JsonResponse({'error': 'New password is required'}, status=400)
            except Exception as e:
                return JsonResponse({'error': 'Invalid request data'}, status=400)
        else:
            return redirect(f"{base_url}/password-reset-confirm/{uidb64}/{token}/")
    else:
        return JsonResponse({'error': 'Invalid link'}, status=400)