import hashlib

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

    # validates sign up        <tr>

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
