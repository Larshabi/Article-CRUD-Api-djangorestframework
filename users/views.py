from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, ListModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import LoginSerializer, RegisterSerializer, EmailVerificationSerializer, LogoutSerializer, ArticleSerializer
from .models import MyUser, Article
from .utils import Util
from django.contrib.sites.shortcuts import get_current_site 
from django.urls import reverse
import jwt
from django.conf import settings
from rest_framework_simplejwt.views import TokenObtainPairView

class RegisterView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    queryset = MyUser.objects.all()
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user = MyUser.objects.get(email=serializer.data["email"])
        token = RefreshToken.for_user(user).access_token
        relativeLink = reverse('verify')
        current_site = get_current_site(request).domain
        absurl = 'http://'+current_site + relativeLink+"?token="+str(token)
        email_body = 'Hi '+ user.username+'\n Please Use the link below to verify your email \n'+ absurl
        data = {
            "email_body":email_body, 'email_subject':"Verify Your Email", 'to_email':user.email,
        }
        Util.send_email(data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class VerifyEmail(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = EmailVerificationSerializer
    def get(self, request):
        token = request.GET.get('token')
        # try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user = MyUser.objects.get(id=payload['user_id'])
        print(user)
        try:
            if not user.is_active:    
                user.is_active = True
                user.save()
                return Response({'message':'Successfully Activated'}, status=status.HTTP_200_OK)
        
        except jwt.ExpiredSignatureError as identifer:
            return Response({"error": "Activation Expired"}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifer:
            return Response({"error":"Decode Error"}, status=status.HTTP_400_BAD_REQUEST)
class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    authentication_classes = [JWTAuthentication]
        
class LogoutView(GenericAPIView):
    permission_classes = [IsAuthenticated] 
    authentication_classes = [JWTAuthentication]
    serializer_class = LogoutSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class ArticleView(GenericAPIView, ListModelMixin):
    queryset = Article.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ArticleSerializer
    
    def get(self, request):
        return self.list(request)
    
class ArticleDetailView(GenericAPIView, CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin):
    queryset = Article.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ArticleSerializer
    lookup_field = 'slug'
    
    def post(self, request):
        return self.create(request)
    def get(self, request, slug):
        return self.retrieve(request, slug)
    def put(self, request, slug):
        return self.update(request, slug)
    def patch(self, request, slug):
        return self.partial_update(request, slug)
    def delete(self, request, slug):
        return self.destroy(request, slug)
    