import bcrypt

username = input("enter username ")
password = input("enter password ")

hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
print(f"{username} = {hashed}")
