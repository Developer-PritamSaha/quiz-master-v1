from application.models.login_model import *

def check_db_integrity():
    '''Checks for Admin and all Roles are initialized\n
    properly or not in the database.'''
    if User.query.filter_by(id=1000).first():
        roles = Role.query.all()
        if (roles[0].id == 2000) and (roles[0].name == "admin") and (roles[1].id == 2001) and(roles[1].name == "user"):
            if Roles_Users.query.filter_by(user_id=1000, role_id=2000).first():
                return True  
    
    return False
