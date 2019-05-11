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
staticPath = os.path.join(os.getcwd(), "finance_manager", "static", "financeManager")
sqlPath = os.path.join(os.getcwd(), "finance_manager", "static", "financeManager", "sql")

# global vars
args = {
    'title': "",
    'form': None,
    'err': {},
    'confirm': {},
    'userName': "",
    'data': {},
    'loggedIn': False,
    'range': None,
    'isEdit': False,
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

# clear notification data
def clearNotificatons():
    global args

    args['confirm'] = {}
    args['err'] = {}

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

                utils.clearData(staticPath)
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

    if checkLogin():
        args['title'] = "Home"
        return render(request, "financeManager/home.html", args)
    else:
        return HttpResponseRedirect('/login/')

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

        data = conn.query("SELECT DISTINCT transactions.amount, transactions.DOT, transactions.businessName, businessInfo.address, businessInfo.state, users.creditCard "
                          "FROM transactions, businessInfo, users WHERE transactions.businessName = businessInfo.businessName  "
                          "AND transactions.userName = '{}'".format(args['userName']))
        trans = utils.df_to_dict(data)
        trans['creditCard'][0] = trans['creditCard'][0][-4:]
        for index, val in enumerate(trans['amount']):
            trans['amount'][index] = format(trans['amount'][index], '.2f')

        # create downloadable csv
        filePath = os.path.join(staticPath, "data", "transactions.csv")
        utils.createCSV(filePath, trans)

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
        err = {}
        confirm = {}
        if "newPass" in args['confirm'].keys():
            confirm = {'newPass': args['confirm']['newPass']}
        print("Confirm", confirm, "Args", args['confirm'])

        if request.method == "POST":
            clearNotificatons()
            keys = request.POST.copy().keys()
            if not args['isEdit'] and "editProfile" in keys: # clicked edit
                args['isEdit'] = True
                return render(request, "financeManager/account.html", args)
            elif "changePassword" in keys:
                return HttpResponseRedirect('/password/')
            else: # submit updates
                args['isEdit'] = False
                data = conn.query("SELECT fullName, creditCard " +
                                    "FROM users WHERE userName = '{}'".format(args['userName']))
                data = utils.df_to_dict(data)
                update = request.POST.copy()

                if update['updateUserName'].strip() != "":
                    userNames = conn.query("SELECT userName FROM users")
                    userNames = utils.df_to_dict(userNames)
                    if update['updateUserName'] not in userNames['userName']:
                        confirm['userName'] = update['updateUserName']
                        conn.callproc("updateUserName", "", args['userName'], update['updateUserName'], isDML=True)
                        args['userName'] = update['updateUserName']
                    else:
                        err['userName'] = True

                if update['updateFullName'].strip() != "":
                    if update['updateFullName'] != data['fullName'][0]:
                        confirm['fullName'] = update['updateFullName']
                        conn.callproc("updateFullName", "", args['userName'], update['updateFullName'], isDML=True)
                    else:
                        err['fullName'] = True

                if update['updateCreditCard'].strip() != "":
                    update['updateCreditCard'] = update['updateCreditCard'].strip()
                    update['updateCreditCard'] = update['updateCreditCard'].replace('-', '')

                    print(update['updateCreditCard'])
                    if update['updateCreditCard'] != data['creditCard'][0] and len(update['updateCreditCard']) == 16:
                        confirm['creditCard'] = update['updateCreditCard'][-4:]
                        conn.callproc("updateCreditCard", "", args['userName'], update['updateCreditCard'], isDML=True)
                    else:
                        err['creditCard'] = True

        args['isEdit'] = False

        # grab data from database
        data = conn.query("SELECT users.fullName, balance.balance, users.creditCard "
                          "FROM users, balance "
                          "WHERE users.userName = balance.userName "
                          "AND users.userName = '{}'".format(args['userName']))

        accountInfo = utils.df_to_dict(data)

        accountInfo['fullName'] = accountInfo['fullName'][0]
        accountInfo['creditCard'] = accountInfo['creditCard'][0][-4:]
        accountInfo['balance'] = format(accountInfo['balance'][0], '.2f')

        args['data'] = accountInfo
        args['err'] = err
        args['confirm'] = confirm

        return render(request, "financeManager/account.html", args)
    else:
        return HttpResponseRedirect('/login/')

# change password page
def changePassword(request):
    global args

    if checkLogin():
        clearNotificatons()
        err = {}
        confirm = {}
        if request.method == "POST" and "submitChanges" in request.POST.copy().keys():
            data = conn.query("SELECT password FROM users WHERE userName = '{}'".format(args['userName']))
            password = utils.df_to_dict(data)['password'][0]
            update = request.POST.copy()
            hashUpdate = utils.hash(update['updatePassword'])

            if len(update['updatePassword'].strip()) > 0:
                if hashUpdate == password:
                    err['oldPass'] = True
                if update['updatePassword'] != update['confirmPassword']:
                    err['confirm'] = True

                if len(err.keys()) == 0:
                    confirm['newPass'] = True
                    args['confirm'] = confirm
                    conn.execute("UPDATE users SET password = '{0}' WHERE userName = '{1}'".format(hashUpdate, args["userName"]))
                    return HttpResponseRedirect('/account/')

        args['err'] = err
        return render(request, "financeManager/password.html", args)
    else:
        return HttpResponseRedirect('/login/')
