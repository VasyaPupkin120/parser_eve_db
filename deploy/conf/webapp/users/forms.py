from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        # fields = ('email', 'username')
        fields = "__all__"

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = get_user_model()
        # fields = ('email', 'username')
        fields = "__all__"
        # fields = UserCreationForm.Meta.fields
