import re


def checking_password(password, verify_password):
    """
        checking for password requirements
    """
    valid_pwd = False
    msg = ""

    password_pattern = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$"
    if password == verify_password:
        if re.match(password_pattern, verify_password):
            msg = 'Passwords meet requirements.'
            valid_pwd = True
        else:
            msg = 'Password requirements: 8 characters long,1 uppercase,1 lowercase, 1 digit,and 1 special character(ie: !@#$)'
            valid_pwd = False
    if password != verify_password:
        msg = 'The passwords do not match.'
        valid_pwd = False

    return {
        "valid_pwd": valid_pwd,
        "msg": msg
    }


def checking_entry(data, users):
    """
        Check if user has valid password
        check if username and email are taken
        #data holds submitted data
        #users is all users in json file
    """
    # user is invalid by default
    valid_user = False

    valid_pwd = checking_password(data["password"], data["password-verify"])
    val_pwd_result = valid_pwd['valid_pwd']

    uname = data['username']
    email = data['email']
    msg = ''
    if val_pwd_result:
        for user in users['users']:
            if uname == user['username']:
                valid_user = False
                msg = 'This username is taken'
                break
            if email == user['email']:
                valid_user = False
                msg = 'This email is taken'
                break
            if not email or not uname:
                valid_user = False
                msg = 'username and email are required'
                break
            if uname != user['username'] and email != user['email']:
                valid_user = True
                msg = ''
        return {"valid-user": valid_user, "msg": msg}

    if not val_pwd_result:
        return {"valid-user": valid_pwd['valid_pwd'], "msg": valid_pwd['msg']}
