import os
from django.conf import settings
from django.shortcuts import render
from .static.financeManager.python.SQLManager import SQLManager
from .static.financeManager.python.utils import utils
from .static.financeManager.python.forms import LoginForm, SignupForm


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

data = {'ander428': 'Password1', 'jwanderson198': 'Password1'}
args = {
    'title': "",
    'form': None,
    'err': {},
    'UserName': "",
}

# login page
def login(request):
    global args
    args['title'] = "Login"

    err = {'UserName': False, 'Password': False}
    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            usr = form.cleaned_data['userName']
            psw = form.cleaned_data['password']

            if usr in data:
                if data[usr] == psw:
                    print("Login successful!")
                    args['UserName'] = usr
                    return home(request)
                else:
                    err['Password'] = True
                    print("Att:", psw, "Act:", data[usr])
            else:
                err['UserName'] = True
                print("Att:", usr)


    args['form'] = LoginForm()
    args['err'] = err
    return render(request, "financeManager/login.html", args)

# signup page
def signup(request):
    global args
    print(data)
    err = {'UserName': False, 'Password': False}
    if request.method == 'POST':
        form = SignupForm(request.POST)

        if form.is_valid():
            usr = form.cleaned_data['userName']
            psw = form.cleaned_data['password']
            cfm = form.cleaned_data['confirmPassword']

            if usr not in data:
                if psw == cfm:
                    data.setdefault(usr, psw)
                    print("Account Created")
                    print(data)
                else:
                    err['Password'] = True
            else:
                err['UserName'] = True
                print("Att:", usr)

    args['form'] = SignupForm()
    args['err'] = err
    return render(request, "financeManager/signup.html", args)

# home page
def home(request):
    global args
    args['title'] = "Home"
    print(args['UserName'])
    return render(request, "financeManager/home.html", args)

# analytics page
def analytics(request):
    global args
    args['title'] = "Analytics"
    return render(request, "financeManager/analytics.html", args)

# transactions page
def trans(request):
    global args
    args['title'] = "Transactions"
    return render(request, "financeManager/transactions.html", args)
