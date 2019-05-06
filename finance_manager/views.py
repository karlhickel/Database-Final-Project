import os
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponseRedirect, FileResponse
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
                    utils.hash(form.cleaned_data['password'])
                ))
                print("Account Created!")
                return HttpResponseRedirect('/login/')
            elif attempt == 1: # userName error
                err['userName'] = True
            elif attempt == 2: # password error
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
        # call stored procedure of getting transactions by state
        data = conn.callproc("stateTransactionCount", ['state','count'], args['userName'])
        data = data.sort_values('count', ascending=False).head(10) # select top 10
        pie = utils.df_to_dict(data)

        # call stored procedure for average Transactions
        data = conn.callproc("averageIncomeExpense", ['pos','neg'], args['userName'], display=True)
        bar = utils.df_to_dict(data)

        # clean data
        bar['neg'] = round(bar['neg'][0]*-1, 2)
        bar['pos'] = round(bar['pos'][0], 2)

        # assign data values
        args['title'] = "Analytics"
        args['range'] = range(0, len(pie['state']))
        args['data'] = {'pie': pie, 'bar': bar}

        return render(request, "financeManager/analytics.html", args)
    else:
        return HttpResponseRedirect('/login/')

# transactions page
def trans(request):
    global args

    if checkLogin():
        args['title'] = "Transactions"

        data = conn.query("SELECT DISTINCT transactions.amount, transactions.DOT, transactions.businessName, businessInfo.address, businessInfo.state "
                          "FROM transactions, businessInfo WHERE transactions.businessName = businessInfo.businessName  "
                          "AND transactions.userName = '{}'".format(args['userName']))
        trans = utils.df_to_dict(data)

        if request.GET.get('downloadCSV'):
            fileName = args['userName'] + "_transactions.csv"
            utils.createCSV(fileName, trans)

        args["data"] = trans
        args["range"] = range(0, len(trans['amount']))

        return render(request, "financeManager/transactions.html", args)
    else:
        return HttpResponseRedirect('/login/')

# account page
def account(request):
    global args

    if checkLogin():
        args['title'] = "Account"

        data = conn.query("SELECT users.fullName, balance.balance, users.creditCard "
                          "FROM users, balance "
                          "WHERE users.userName = balance.userName "
                          "AND users.userName = '{}'".format(args['userName']), display=True)
        accountInfo = utils.df_to_dict(data)
        args['data'] = accountInfo

        return render(request, "financeManager/account.html", args)
    else:
        return HttpResponseRedirect('/login/')
