from django.urls import path
from . import views

app_name="financeManager"
urlpatterns = [
    # dictate the possible url paths of the app
    path('', views.home, name='financials-home'),
    path('home/', views.home, name='redirect-home'),
    path('login/', views.login, name='auth-page'),
    path('signup/', views.signup, name='signup-page'),
    path('analytics/', views.analytics, name='analytics-page'),
    path('transactions/', views.trans, name='trans-page'),
    path('account/', views.account, name='acct-page'),
    path('password/', views.changePassword, name='change-pass')
]
