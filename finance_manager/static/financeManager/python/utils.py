import hashlib
import csv
import os

class utils:
    # hashes passwords to compare to db
    def hash(password):
        result = hashlib.sha224(password.encode())
        return result.hexdigest()

    # converts pandas df to a dictionary
    def df_to_dict(df):
        df.dropna(inplace=True)             # drop null vals to avoid errors
        return df.to_dict(orient='list')    # assign lists to keys in dict

    # validate login
    def validLogin(form, conn):
        # store form data
        usr = form.cleaned_data['userName']
        pwd = form.cleaned_data['password']

        # grab user and password from database
        data = conn.query("SELECT userName, password " +
                          "FROM users WHERE userName = '{}'".format(usr))
        login = utils.df_to_dict(data)

        if login['userName']: # found user
            if utils.hash(pwd) == login['password'][0]: # check password
                print("Login successful!")
                return 0 # valid
            else: # password doesn't match
                return 2
        else: # userName not found
            return 1

    # validates sign up
    def validSignUp(form, conn):
        # store form data
        usr = form.cleaned_data['userName']
        pwd = form.cleaned_data['password']
        cfm = form.cleaned_data['confirmPassword']

        # check if user is in database
        data = conn.query("SELECT userName " +
                          "FROM users WHERE userName = '{}'".format(usr))
        login = utils.df_to_dict(data)

        if login['userName']: # user already exists
            return 1
        else:
            if pwd != cfm:
                return 2 # passwords don't match
            else:
                return 0 # valid

    # write csv
    def createCSV(filePath, dict):
        columns = []

        for key in dict.keys():
            columns.append(key)

        with open(filePath, 'w') as file:
            writer = csv.DictWriter(file, fieldnames=columns)

            for i in range(0, len(dict[columns[0]])):
                row = {}
                for col in columns:
                    row[col] = dict[col][i]
                writer.writerow(row)

    # delete csvs
    def clearData(path):
        transactions = os.path.join(path, "data", "transactions.csv")

        if os.path.isfile(transactions):
            try:
                os.remove(transactions)
                print("file removed")
            except OSError:
                pass
