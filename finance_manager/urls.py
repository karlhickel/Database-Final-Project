from django.urls import path
from . import views

app_name="financeManager"
urlpatterns = [
    # dictate the possible url paths of the app
    path('', views.login, name='financials-home'),
    path('login/', views.login, name='auth-page'),
    path('signup/', views.signup, name='signup-page'),
    path('analytics/', views.analytics, name='analytics-page'),
    path('transactions/', views.trans, name='trans-page')
]
