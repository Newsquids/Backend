"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
# import orjson

# class JSONRenderer(BaseRenderer):
#     media_type = "application/json"
#     def render(self, request, data, *, response_status):
#         return orjson.dumps(data)

from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
from news.api import router as news_router
from user.api import router as user_router
from ninja.renderers import BaseRenderer

api = NinjaAPI()
api.add_router("news", news_router)
api.add_router("user", user_router)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]

