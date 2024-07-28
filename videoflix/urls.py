from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from user.views import UserView, LoginView, LogoutView, activate, request_password_reset, password_reset_confirm
from backend.views import VideoList, VideoDetail, VideoByGenreList



urlpatterns = [
    path('admin/', admin.site.urls),
    path("__debug__/", include("debug_toolbar.urls")),
    path('django-rq/', include('django_rq.urls')),
    path('register/', UserView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user/', UserView.as_view(), name='user'),
    path('videos/', VideoList.as_view(), name='video-list'),
    path('videos/<int:pk>/', VideoDetail.as_view(), name='video-detail'),
    path('videos/genre/<str:genre>/', VideoByGenreList.as_view(), name='video-by-genre'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('request-password-reset/', request_password_reset, name='request-password-reset'),
    path('password-reset-confirm/<uidb64>/<token>/', password_reset_confirm, name='password-reset-confirm'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
