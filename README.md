# Database Management Final Project

## Authors
**Joshua Anderson** - Computer Science, Junior  
**Karl Hickel** - Data Analytics, Junior

## Instructions
This is a Django web server project. In order to run on a local machine you *must* have the packages below installed and ***python 3***. To start the server and run the project, navigate to the directory with ***manage.py***. This should be the root directory. Then, run this in the command line:
```bash
python manage.py runserver
```
## Required Packages
Django can run on several different versions of python, but to ensure that the project runs smoothly, ***please use python 3.x***. We ran this project with python 3.5.

Python Django:
```bash
pip install django
```
Pandas:
```bash
pip install pandas
```
MySQL Connecor:
```bash
pip install mysql.connector
```

## Queries in the program
| Requirement | Location |
| --- | --- |
| 1. Print/display records from your database/tables.  | views.py (Line 184-186) |
| 2. Query for data/results with various parameters/filters  | utils.py (Line 84-100), views.py (Line 220-223) |
| 3. Create a new record  | views.py (Line 226-232) |
| 4. Delete records (soft delete function would be ideal)  | views.py (Line 295-299) |
| 5. Update records  | views.py (Line 300-333) |
| 6. Make use of transactions (commit & rollback)  | views.py (Line 113-127) |
| 7. Generate reports that can be exported (excel or csv format) | views.py (Lines 253-256) |
| 8. One query must perform an aggregation/group-by clause  | views.py (Line 153) - procedure stateTransactionCount() |
| 9. One query must contain a sub-query.  | views.py (Line 159) - procedure averageIncomeExpense() |
| 10. Two queries must involve joins across at least 3 tables.  | views.py (Lines 184-186) - transactions & (Lines 338) - procedure viewAccount() |
| 11. Enforce referential integrality (Constraints)  | DatabaseCreation.sql (Lines 1-39) |
| 12. Include Database Views, Indexes | DatabaseCreation.sql (Lines 143-152) - view, DatabaseCreation.sql (Lines 93-94) - index |

## Database Schema
[Schema Img](https://raw.githubusercontent.com/karlhickel/Database-Final-Project/blob/master/Database%20Files/Schema.png)


## Directories/Files with SQL queries
- [finance_manager/views.py](https://github.com/karlhickel/Database-Final-Project/blob/master/finance_manager/views.py)
- [finance_manager/static/financeManager/python/utils.py](https://github.com/karlhickel/Database-Final-Project/blob/master/finance_manager/static/financeManager/python/utils.py)
- [Database/DatabaseCreation.sql](https://github.com/karlhickel/Database-Final-Project/blob/master/Database/DatabaseCreation.sql)

## References
These are a list of references that were used to assist in the making of this web application (mainly styling references):
- https://developers.google.com/chart/interactive/docs/reference
- https://codepen.io/blindpiggy/pen/QQzRYY
