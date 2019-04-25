from django.urls import path
from . import views

urlpatterns = [
    # dictate the possible url paths of the app
    path('', views.home, name='financials-home'),
    path('dev/', views.dev, name='development-page'),
    path('login/', views.login, name='auth-page'),
    path('analytics/', views.analytics, name='analytics-page'),
    path('transactions/', views.trans, name='trans-page')
]
