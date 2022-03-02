from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.template.defaultfilters import slugify
from rest_framework_simplejwt.tokens import RefreshToken

class MyUserManager(BaseUserManager):
    def create_user(self, username, email, firstName, password, **otherfields):
        user = self.model(
            email = self.normalize_email(email),
            username =username,
            firstName = firstName,
            **otherfields
        )
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, username, email, password, **otherfields):
        otherfields.setdefault('is_admin', True)
        otherfields.setdefault('is_staff', True)
        otherfields.setdefault('is_superuser', True)
        otherfields.setdefault('is_active', True)
        user = self.create_user(
            email = email,
            username =username,
            password = password,
            **otherfields
        )
        return user

class MyUser(AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name_plural = "My Users"
        verbose_name = "My User"
        
    firstName = models.CharField(max_length=200)
    lastName = models.CharField(max_length=200)
    username = models.CharField(max_length=200, unique=True, db_index=True)
    email = models.EmailField(max_length=250, unique=True, db_index=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    
    objects = MyUserManager()
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "firstName"]
    
    def __str__(self):
        return self.username 
    # def tokens(self):
    #     refresh = RefreshToken.for_user(self)
    #     return {
    #         'refresh': str(refresh),
    #         'access': str(refresh.access_token),
    #     }
class Article(models.Model):
    class Meta:
        verbose_name_plural = "Articles"
        verbose_name = "Article"
    author = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    slug = models.SlugField(null=True, blank=True)
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.title)
        super(Article, self).save(*args, **kwargs)