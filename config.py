import base64

email = 'guylavian4@gmail.com'
api_token = 'ATATT3xFfGF090iBXTMnF8hUGIxsEFEI3RdKkJ'
credentials = f"{email}:{api_token}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()

print(encoded_credentials)
