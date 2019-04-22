from django.shortcuts import render
from django.http import HttpResponse

# handle traffic from homepage
def home(request):
    return render(request, "financeManager/home.html", users)

def dev(request):
    return render(request, "financeManager/dev.html")
