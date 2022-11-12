def checking_password(password, verify_password):
    """
        checking for password requirements
    """
    test = True
    msg = ""
    count = 0
    for char in password:
        if char in "[@_!#$%^&*()<>?/|}{~:=]":
            count = count + 1
            print(password)
            print(count)
    if count == 0:
        test = False
        msg = "Passwords need at least one special character"
        print(password)
        print(count)
    if len(password) < 12:
        test = False
        msg = "Passwords need at least 12 characters"

    if not any(char.isdigit() for char in password):
        test = False
        msg = "Passwords need at least one number"
    if not any(char.isupper() for char in password):
        test = False
        msg = "Password need at least one upper character"
    if not any(char.islower() for char in password):
        test = False
        msg = "Password need at least one lower character"
    if not password == verify_password:
        test = False
        msg = "Password did not match"

    return {
        "test": test,
        "msg": msg
    }


def checking_entry(data, users):
    """
        checking user's submission entry
    """
    test = checking_password(
        data["password"],
        data["password-verify"]
    )["test"]
    msg = checking_password(
        data["password"],
        data["password-verify"]
    )["msg"]
    if not test:
        test = False
    if not "@" in data["email"]:
        test = False
        msg = "Please enter a valid email address"
    if data["username"] == "":
        test = False
        msg = "Please enter a username"
    for user in users:
        if user["username"].lower() == data["username"].lower():
            test = False
            msg = "that username is already taken"
    return {
        "test": test,
        "msg": msg
    }