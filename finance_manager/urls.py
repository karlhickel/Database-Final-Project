from django.urls import path
from . import views

# dictate the possible url paths of the app
urlpatterns = [
    path('', views.home, name='financials-home'),
    path('dev/', views.dev, name='development-page'),
    path('login/', views.login, name='auth-page')
]
