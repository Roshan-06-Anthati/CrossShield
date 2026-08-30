import pandas as pd

df = pd.read_csv('data/phishing_email.csv')
print(df.columns)
print(df.head())
print(df.shape)