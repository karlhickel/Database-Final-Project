from django.shortcuts import render
from .static.financeManager.python.SQLManager import SQLManager
from django.conf import settings
import os

# create MySQL connection
conn = SQLManager("mysql", "cpsc408", user="rene", password="databasePass", host="35.199.189.236", debug=False) # SQL

# get path for sql files
sqlPath = os.path.join(os.getcwd(), "finance_manager", "static", "financeManager", "SQL")

# execute sql
conn.execute(os.path.join(sqlPath, "test.sql"))
data = conn.query("SELECT * from info")#, display=True)
conn.dropTable("info")

records = []

for index, row in data.iterrows():
    records.append(
        {
            'userName': row['userName'],
            'content': row['content']
        }
    )
### Functions for rendering each page ###

# login page
def login(request):
    return render(request, "financeManager/login.html", {'title': 'Log In'})

# home page
def home(request):
    return render(request, "financeManager/home.html", {'title': 'Home'})

# developement page
def dev(request):
    context = {
        'records': records
    }
    return render(request, "financeManager/dev.html", context)
