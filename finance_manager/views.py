import os
import datetime
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
    'file': "",
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

        # query bubblechart data
        data = conn.query("SELECT count(ID) as count, MONTH(DOT) as month, YEAR(DOT) as year, sum(amount) as amount " +
                        "FROM transactions t, businessInfo b " +
                        "WHERE userName = 'ander428' AND t.businessName = b.businessName " +
                        "GROUP BY year, month")
        bubble = utils.df_to_dict(data)
        for key,val in bubble.items():
            print(key,":", val)

        # call stored procedure of getting transactions by state
        data = conn.callproc("stateTransactionCount", ['state','count'], args['userName'])
        data = data.sort_values('count', ascending=False).head(10) # select top 10
        pie = utils.df_to_dict(data)
        print(pie)

        # call stored procedure for average Transactions
        data = conn.callproc("averageIncomeExpense", ['pos','neg'], args['userName'], display=True)
        bar = utils.df_to_dict(data)


        # clean data
        bar['neg'] = round(bar['neg'][0]*-1, 2)
        bar['pos'] = round(bar['pos'][0], 2)

        # assign data values
        args['title'] = "Analytics"
        args['range'] = {'pie': range(0, len(pie['state'])), 'bubble': range(0,len(bubble['count']))}
        args['data'] = {'pie': pie, 'bar': bar, 'bubble': bubble}

        return render(request, "financeManager/analytics.html", args)
    else:
        return HttpResponseRedirect('/login/')

# transactions page
def trans(request):
    global args

    if checkLogin():
        args['title'] = "Transactions"

        # predefine transactions query
        transactionQuery = str("SELECT DISTINCT transactions.amount, transactions.DOT, transactions.businessName, businessInfo.address, businessInfo.state, users.creditCard "
                           + "FROM transactions, businessInfo, users WHERE transactions.businessName = businessInfo.businessName  "
                           + "AND transactions.userName = '{}' AND transactions.userName = users.userName".format(args['userName']))

        selected = {}

        # filter is submitted OR Transaction added
        if request.method == 'POST':
            keys = request.POST.copy()

            # add transaction params
            amount = 0
            businessName = ''
            address = ''
            state = ''

            addBusiness = False

            for key, value in keys.items():
                if value != '':
                    # insert transactions
                    if key == 'insertAmount':
                        amount = value
                    elif key == 'insertBusinessName':
                        business = conn.query("SELECT businessName FROM businessInfo")
                        business = utils.df_to_dict(business)

                        if value not in business['businessName']:
                            businessName = value
                            addBusiness = True
                    elif key == 'insertBussinessAddress' and addBusiness:
                        address = value
                    elif key == 'insertState' and addBusiness:
                        state = value

                    # filters
                    condition = utils.transactionFilter(key, value)
                    if condition != "":
                        selected[key] = value
                        transactionQuery += condition

            # send to new transaction to database
            if amount != 0:
                conn.callproc("updateTransactions", [], amount, businessName, args['userName'], isDML=True)
                if addBusiness:
                    conn.callproc("updateInsertBusiness", [], businessName, address, state, isDML=True)

        data = conn.query(transactionQuery)
        trans = utils.df_to_dict(data)

        # if you cant find creditCard
        if not trans['creditCard']:
            creditCard = conn.query("SELECT creditCard FROM users WHERE userName = '{}'".format(args['userName']))
            creditCard = utils.df_to_dict(creditCard)['creditCard']
            trans['creditCard'] = creditCard
        trans['creditCard'][0] = trans['creditCard'][0][-4:]

        for index, val in enumerate(trans['amount']):
            trans['amount'][index] = format(trans['amount'][index], '.2f')

        # create downloadable csv
        d = datetime.datetime.today()
        fileName = "transactions_{}.csv".format(d.isoformat())
        filePath = os.path.join(staticPath, "data", fileName)
        utils.createCSV(filePath, trans)

        # query distinct years and states for filter
        years = conn.query("SELECT DISTINCT YEAR(DOT) as year FROM transactions")
        years = utils.df_to_dict(years)
        yearSet = set(years['year'])
        states = conn.query("SELECT DISTINCT state FROM businessInfo, transactions WHERE userName = '{}'".format(args['userName']) +
        " AND transactions.businessName = businessInfo.businessName")
        states = utils.df_to_dict(states)
        stateSet = sorted(set(states['state']))

        args["data"] = {"trans": trans, "years": yearSet, "states": stateSet, "selected": selected}
        args["range"] = range(0, len(trans['amount']))
        args["file"] = fileName

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
        data = conn.callproc("viewAccount", ["fullName", "balance", "creditCard", "DOT"], args['userName'])
        accountInfo = utils.df_to_dict(data)

        # clean data
        accountInfo['fullName'] = accountInfo['fullName'][0]
        accountInfo['creditCard'] = accountInfo['creditCard'][0][-4:]
        accountInfo['balance'] = format(accountInfo['balance'][0], '.2f')
        accountInfo['DOT'] = accountInfo['DOT'][0]

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
