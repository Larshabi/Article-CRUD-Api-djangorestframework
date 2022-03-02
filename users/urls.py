from django.urls import path
from .views import LoginView, RegisterView, VerifyEmail, LogoutView, ArticleView, ArticleDetailView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
urlpatterns = [
    path('register/', RegisterView.as_view(), name="register"),
    path('verify-email/', VerifyEmail.as_view(), name="verify"),
    path('login/', LoginView.as_view(), name="token_obtain_pair"),
    path('login/refresh/', TokenRefreshView.as_view(), name="token_refresh"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('article/', ArticleView.as_view(), name="articles"),
    path('article/<slug:slug>/', ArticleDetailView.as_view(), name="article")
    
]
