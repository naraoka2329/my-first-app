"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from django.contrib.auth import views

from django.views.generic.base import RedirectView

import file_upload.views as file_upload
import video.views as video

from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', views.LoginView.as_view(), name='login'),
    path('accounts/logout/', views.LogoutView.as_view(next_page='/'), name='logout'),
    path('', include('movie.urls')),
    #file_upload
    path('success/url/',file_upload.success),
    path('file_upload/', include('file_upload.urls')),
    path('', RedirectView.as_view(url='/file_upload/')),
    #video
    path('video/', include('video.urls')),
]

#ストレージ領域へURLからアクセス
#いらない？
#urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
