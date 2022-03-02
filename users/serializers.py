from rest_framework import serializers
from .models import MyUser, Article
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.exceptions import AuthenticationFailed


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(label = "Password",  style={"input_type":"password"}, write_only=True)
    password2 = serializers.CharField(label = "Confirm Password", style={"input_type":"password"}, write_only=True)
    firstName = serializers.CharField(label = "First Name")
    lastName = serializers.CharField(label = "Last Name")
    class Meta:
        model =MyUser
        fields = [
            "email",
            "username",
            "firstName",
            "lastName",
            "password",
            "password2",
        ]
        
    def validate(self,attrs):
        email = attrs.get("email","")
        username = attrs.get("username", "")
        password = attrs.get("password", "")
        password2 = attrs.get("password2", "")
        if MyUser.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email already exists")
        if MyUser.objects.filter(username=username).exists():
            raise serializers.ValidationError("Username already exists")
        if password and password2 and password != password2:
            raise serializers.ValidationError("Passwords do not match")
        if len(password) < 8 and len(password2) < 8:
            raise serializers.ValidationError("Password must contain at least 8 characters")
        return super().validate(attrs)
    def create(self, validated_data):
        # password = validated_data["password"]
        user = MyUser.objects.create_user(
            email = validated_data["email"],
            username = validated_data["username"],
            firstName = validated_data["firstName"],
            lastName = validated_data["lastName"],
            password = validated_data["password"],
        )
        # user.set_password(password)
        return user
class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password')
        user = authenticate( email=email, password=password)
        print(user)
        if not user:
            raise AuthenticationFailed("Invalid Username/Password")
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data["email"] = self.user.email
        data["username"] = self.user.username
        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)
        return data
    # def validate(self, attrs):
    #     email = attrs.get('email', '')
    #     password = attrs.get('password')
    #     user = authenticate( email=email, password=password)
    #     print(user)
    #     if not user:
    #         raise AuthenticationFailed("Invalid Username/Password")
    #     return {
    #         "email": user.email,
    #         "username": user.username,
    #         "tokens": user.tokens
    #     }

class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=555, read_only=True)
    
    class Meta:
        model = MyUser
        fields = ["token"]
        
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    
    default_error_message = {
        'bad token': 'Token is expired or invalid'
    }
    
    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs
    
    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('bad token')
            
class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = [
            "id",
            "author",
            "title",
            "content"
                  ]