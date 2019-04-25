class utils:
    # converts pandas df to a dictionary
    def df_to_dict(df):
        df.dropna(inplace=True)             # drop null vals to avoid errors
        return df.to_dict(orient='list')    # assign lists to keys in dict
