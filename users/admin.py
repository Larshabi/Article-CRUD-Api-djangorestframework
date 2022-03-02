from django.contrib import admin
from .models import MyUser, Article
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from rest_framework_simplejwt.token_blacklist.admin import OutstandingTokenAdmin
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken



class MyUserAdminForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget = forms.PasswordInput)
    class Meta:
        model = MyUser
        fields = [
            "email",
            "username",
            "firstName",
            "lastName",
            "password1",
            "password2",
        ]
        
    def clean_email(self):
        email =self.cleaned_data["email"]
        if MyUser.objects.filter(email=email).exists():
            raise ValidationError("email already exists")
        return email
    
    def clean_username(self):
        username = self.cleaned_data["username"]
        if MyUser.objects.filter(username=username):
            raise ValidationError("username already exists")
        return username
        
    def clean_password2(self):
        password1 =self.cleaned_data["password1"]
        password2 = self.cleaned_data["password2"]
        if len(password1) < 8 and len(password2) < 8:
            raise  ValidationError("Password must not be less than 8 characters")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not Match")
        
        return password2
    
    def save(self, commit=True):
        user = super(MyUserAdminForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        user.username = self.cleaned_data["username"]
        user.firstName = self.cleaned_data["firstName"]
        user.lastName = self.cleaned_data["lastName"]
        user.set_password(self.cleaned_data["password1"])
        
        if commit:
            user.save()
        return user
    
    
class MyUserAdminChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()
    
    class Meta:
        model = MyUser
        fields = '__all__'
        
    def clean_password(self):
        return self.initial["password"]
        
    


class MyUserAdmin(BaseUserAdmin):
    form = MyUserAdminChangeForm
    add_form = MyUserAdminForm
    ordering = ["email", 'username']
    list_display = ["email", "username", "is_active"]
    list_filter = ('is_admin',)
    filter_horizontal = ()
    fieldsets = (
        (None, {'fields':('username', 'email', 'password',)}),
        ('About', {'fields':('firstName', 'lastName',)}),
        ('Permissions', {'fields':('is_active', 'is_superuser', 'is_admin', 'is_staff',)})
    )
    add_fieldsets = (
        (None, {'fields':('username', 'email', 'password1', 'password2')}),
        ('About', {'fields':('firstName', 'lastName',)}),
        ('Permissions', {'fields':('is_active', 'is_superuser', 'is_admin', 'is_staff',)})
    )

admin.site.register(MyUser, MyUserAdmin)

class OutstandingTokenAdmin(OutstandingTokenAdmin):
    
    def has_delete_permission(self, *args, **kwargs):
        return True
    
admin.site.unregister(OutstandingToken)
admin.site.register(OutstandingToken, OutstandingTokenAdmin)

class ArticleAdmin(admin.ModelAdmin):
    readonly_fields = ["slug"]
    list_display = ["id",
                    "title",
                    "author"
                    ]
    
admin.site.register(Article, ArticleAdmin)