from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    """
    A form that creates a new CustomUser with an email, inheriting from UserCreationForm.
    Attributes:
        model (CustomUser): The user model that is being used.
        fields (tuple): The field(s) to be included in the form.
    """
    class Meta:
        model = CustomUser
        fields = ('email')
        
class CustomUserChangeForm(UserChangeForm):
    """
    A form for updating an existing CustomUser's email, inheriting from UserChangeForm.
    Attributes:
        model (CustomUser): The user model that is being used.
        fields (tuple): The field(s) to be included in the form.
    """
    class Meta:
        model = CustomUser
        fields = ('email')