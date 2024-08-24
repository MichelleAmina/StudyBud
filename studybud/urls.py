from django.contrib import admin
from django.urls import path, include 

urlpatterns = [
    path('admin/', admin.site.urls),
    # every url that matches an empty string, send the user to base folder, urls file
    path('', include('base.urls'))
]
