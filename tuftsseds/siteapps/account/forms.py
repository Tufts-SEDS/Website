from django import forms
from django.core.validators import validate_email
from tuftsseds.siteapps.main.models import BaseSEDSMember, Chapters


class BaseRegistrationForm(forms.ModelForm):

    name = forms.CharField(
        label='Enter your full name', min_length=4, max_length=50, help_text='Required')
    email = forms.EmailField(label='Enter your Tufts email', max_length=100, help_text='Required', 
        error_messages={'required': 'You will need to enter an email'})
    chapter_affiliation = forms.ModelMultipleChoiceField(queryset=Chapters.objects.all(), required=True, 
                                                         widget=forms.CheckboxSelectMultiple)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password', widget=forms.PasswordInput)

    class Meta:
        model = BaseSEDSMember
        fields = ('email', 'name', 'chapter_affiliation')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords do not match.')
        return cd['password2']

    def clean_email(self):
        email = self.cleaned_data['email']
        if BaseSEDSMember.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'The provided email is already in use')
        if "tufts.edu" not in email:
            raise forms.ValidationError(
                'Email must be Tufts affiliated')
        return email
    
    # Basic overrides to change the css of the form when rendered
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update(
            {'class': 'input-text', 'placeholder': 'John Doe'})
        self.fields['email'].widget.attrs.update(
            {'class': 'input-text', 'placeholder': 'johndoe@tufts.edu'})
        self.fields['password'].widget.attrs.update(
            {'class': 'input-text', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update(
            {'class': 'input-text', 'placeholder': 'Confirm Password'})



class LoginForm(forms.Form):
    email = forms.EmailField(label='Enter your Tufts email', max_length=100, help_text='Required', 
        error_messages={'required': 'You will need to enter an email'})
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        validate_email(email)
        return email
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update(
            {'class': 'input-text', 'placeholder': 'johndoe@tufts.edu', 
                'required pattern': '[^@]+@[^@]+.[a-zA-Z]{2,6}'})
        self.fields['password'].widget.attrs.update(
            {'class': 'input-text', 'placeholder': 'Password', 'id': "login_id_password"})
        
# class LoginForm(AuthenticationForm):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['username'].widget.attrs.update(
#             {'class': 'input-text', 'placeholder': 'johndoe@tufts.edu', 
#                 'required pattern': '[^@]+@[^@]+.[a-zA-Z]{2,6}'})
#         self.fields['password'].widget.attrs.update(
#             {'class': 'input-text', 'placeholder': 'Password', 'id': "login_id_password"})

#     # The username field is just the email field, it is named this was to overwrite the username field in AuthenticationForm
#     username = forms.EmailField(label='Enter your Tufts email', max_length=100, help_text='Required', 
#         error_messages={'required': 'You will need to enter an email'})
#     password = forms.CharField(label='Password', widget=forms.PasswordInput)
    