from flask_security.utils import verify_password
from application.models.login_model import User
from email_validator import validate_email, EmailNotValidError

def authenticate_user(email, entered_passwd):
    """Authenticate the user credentials and will return a tuple -\n 
        (True, user_obj) if the auth is valid, else \n
        (False, -1) if the auth is invalid"""
    valid = valid_email(email)
    flag = True
    if not valid[0]:
        valid_user = User.query.filter_by(email=email).first()
        if valid_user and valid_user.id == 1000: # only for quiz master
            if verify_password(entered_passwd, valid_user.password):
                return (True, valid_user)
        else:
            # print(f'<! Invalid Email: {valid[1]} >')
            flag = False
            # return (False, -1)
    if flag:
        temp_email = email.lower()
        user = User.query.filter_by(email=temp_email).first()
        if user and verify_password(entered_passwd, user.password):
            return (True, user)
        
    return (False, -1)


def valid_email(email):
    try:
        v = validate_email(email) 
        return(True, "Email valid")
    except EmailNotValidError as e:
        return(False, str(e))
