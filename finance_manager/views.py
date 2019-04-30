import os
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponseRedirect
from .static.financeManager.python.SQLManager import SQLManager
from .static.financeManager.python.utils import utils
from .static.financeManager.python.forms import LoginForm, SignupForm


# create MySQL connection
conn = SQLManager("mysql", "FinalProject", user="rene", password="LNDz8ekX52GgTm5", host="35.199.189.236", debug=False) # SQL

# get path for sql files
sqlPath = os.path.join(os.getcwd(), "finance_manager", "static", "financeManager", "SQL")

# global vars
args = {
    'title': "",
    'form': None,
    'err': {},
    'userName': "",
    'data': {},
    'loggedIn': False,
    'range': None
}

# check if user is logged in
def checkLogin():
    global args

    # set userName to empty if logged out
    if not args['loggedIn']:
        args['userName'] = ""

    # don't allow user to be logged in without a userName
    elif args['loggedIn'] and not args['userName']:
        args['loggedIn'] = False

    return args['loggedIn']

### Functions for rendering each page ###

# login page
def login(request):
    global args

    err = {} # stores if fields are valid

    # set global vals
    args['title'] = "Login"
    args['loggedIn'] = False
    args['userName'] = ""

    conn.query("SELECT * FROM users", display=True)

    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            # default errors to false
            err = {'userName': False, 'password': False}

            attempt = utils.validLogin(form, conn)
            if attempt == 0:
                args['userName'] = form.cleaned_data['userName']
                args['loggedIn'] = True
                return HttpResponseRedirect('/transactions/')
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

    # set global vals
    args['title'] = "SignUp"
    args['loggedIn'] = False
    args['userName'] = ""

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
                return HttpResponseRedirect('/login/')
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

    if checkLogin():
        args['data'] = {'pie': {'test1': .4, 'test2': .6}}
        args['title'] = "Analytics"
        return render(request, "financeManager/analytics.html", args)
    else:
        return HttpResponseRedirect('/login/')

# transactions page
def trans(request):
    global args

    if checkLogin():
        args['title'] = "Transactions"

        data = conn.query("SELECT DISTINCT transactions.amount, transactions.DOT, transactions.businessName, businessInfo.address, businessInfo.state " +
        "FROM transactions, businessInfo WHERE transactions.businessName = businessInfo.businessName " +
        "AND transactions.userName = '{}'".format(args['userName']))
        trans = utils.df_to_dict(data)
        args["data"] = trans
        args["range"] = range(0, len(trans['amount']))

        return render(request, "financeManager/transactions.html", args)
    else:
        return HttpResponseRedirect('/login/')
