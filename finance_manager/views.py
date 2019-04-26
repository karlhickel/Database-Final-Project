import os
from django.conf import settings
from django.shortcuts import render
from .static.financeManager.python.SQLManager import SQLManager
from .static.financeManager.python.utils import utils
from .static.financeManager.python.forms import LoginForm



# create MySQL connection
conn = SQLManager("mysql", "FinalProject", user="rene", password="LNDz8ekX52GgTm5", host="35.199.189.236", debug=False) # SQL

# get path for sql files
sqlPath = os.path.join(os.getcwd(), "finance_manager", "static", "financeManager", "SQL")

# execute sql
# conn.execute(os.path.join(sqlPath, "test.sql"))
# data = conn.query("SELECT * from userTable", display=True)
# data = utils.df_to_dict(data)
# print(data)

### Functions for rendering each page ###

# login page
def login(request):
    form = LoginForm()
    return render(request, "financeManager/login.html", {'title': 'Log In', 'form': form})

# home page
def home(request):
    return render(request, "financeManager/home.html", {'title': 'Home'})

# analytics page
def analytics(request):
    return render(request, "financeManager/analytics.html", {'title': 'Analytics'})

# transactions page
def trans(request):
    return render(request, "financeManager/transactions.html", {'title': 'Transactions'})

# developement page
def dev(request):
    context = {
        'records': records
    }
    return render(request, "financeManager/dev.html", context)
