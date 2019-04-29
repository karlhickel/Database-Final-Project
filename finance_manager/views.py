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

args = {
    'title': "",
    'form': None,
    'err': {},
    'userName': "",
    'data': {}
}

# login page
def login(request):
    global args
    args['title'] = "Login"

    err = {}
    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            # default errors to false
            err = {'userName': False, 'password': False}

            attempt = utils.validLogin(form, conn)
            if attempt == 0:
                args['userName'] = form.cleaned_data['userName']
                return home(request)
            elif attempt == 1: # userName error
                err['userName'] = True
            elif attempt == 2: # password error
                err['password'] = True

    args['form'] = LoginForm()
    args['err'] = err
    return render(request, "financeManager/login.html", args)

# signup page
def signup(request):
    global args

    err = {} # stores if fields are valid
    if request.method == 'POST':
        form = SignupForm(request.POST) # grabs form

        if form.is_valid():
            # default errors to false
            err = {'userName': False, 'password': False}

            attempt = utils.validSignUp(form, conn)
            print("ATTEMPT:",attempt)
            if attempt == 0: # create user
                conn.execute("INSERT INTO users(userName, password) " +
                "VALUES('{0}','{1}')".format(
                    form.cleaned_data['userName'],
                    form.cleaned_data['password']
                ))
                print("Account Created!")
                return login(request)
            elif attempt == 1: # userName error
                err['userName'] = True
            elif attempt == 2: # password error
                print("got here")
                err['password'] = True

    args['form'] = SignupForm()
    args['err'] = err
    return render(request, "financeManager/signup.html", args)

# home page
def home(request):
    global args
    args['title'] = "Home"
    print(args['userName'])
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

    data = conn.query(os.path.join(sqlPath, "transactions.sql"))
    trans = utils.df_to_dict(data)
    args["data"] = trans
    return render(request, "financeManager/transactions.html", args)
