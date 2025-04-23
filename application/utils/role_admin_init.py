# Generate a default id and password for the admin user and initialize the database with the admin user.

import os
import uuid
import random
from flask_security.utils import hash_password
from application.models.login_model import User, Role, Roles_Users
from ..db_base import db

letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
symbols = ['!', '#', '$', '%', '&', '^', '*', '+']

def generate_admin_password():
    length = 12
    password = ""

    for x in range(0, length):
        if (x < 4):
            rand_index = random.randint(0,len(letters)-1)
            password = password + letters[rand_index]
    
        if (x < 4):
            rand_index = random.randint(0,len(symbols)-1)
            password = password + symbols[rand_index]
        
        if (x < 4):
            rand_index = random.randint(0,len(numbers)-1)
            password = password + numbers[rand_index]
        
    shuffle_password = "".join(random.sample(password,len(password)))

    #print(f"\n|>> Your {length} character long password is : {shuffle_password}\n")
    return shuffle_password

def generate_admin_id():
    id="Master"
    pre_code="".join(random.choice(numbers) for _ in range(4))
    post_code="".join(random.choice(letters) for _ in range(4))
    return (id+"@"+pre_code+post_code)

def save_admin_credentials(file_path, email, password, flag=0):
    if (not os.path.exists(file_path)) or (flag == 1):
        with open(file_path, "w") as f:
            f.write(">> QuizMaster Default Admin Credentials\n")
            f.write("#################################################\n\n")
            f.write("**Note: This file contains the default admin credentials for the QuizMaster application, which has been initialized along with the first time database initialization. Do not share or delete this file.**\n\n") 
            # f.write("*** If you have already reset the admin credentials, you can delete this file. ***\n\n")

            f.write(f"Default Admin Email: {email}\n")
            f.write(f"Default Admin Password: {password}\n\n")
            f.write("#################################################\n\n")
        # print(f"Admin credentials saved at {file_path}")
    else:
        print(f">> Admin credentials file already exists at '{file_path}'")

# def get_admin_credentials(file_path):
#     if os.path.exists(file_path):
#         with open(file_path, "r") as f:
#             return f.read()
#     return None

def initialize_role_admin(is_active=True):
    g_id = generate_admin_id()
    passwd = generate_admin_password()
    flag = 0
    try:
        existing_admin = User.query.filter_by(id=1000).first()
        # Admin Initialization
        if existing_admin:
            print(">> Admin already initialized.")
            if not os.path.exists("./database/admin_credentials.txt"):
                save_admin_credentials("./database/admin_credentials.txt", existing_admin.email, existing_admin.password)
                print('>> Admin credentials file reinitialized, exists at "./database/admin_credentials.txt"')
            else:
                print('>> Admin credentials file already exists at "./database/admin_credentials.txt"')
            #print(get_admin_credentials("./database/admin_credentials.txt"))
            flag = 1
        else:
            admin = User(
                id = 1000,
                email = g_id,
                password = hash_password(passwd),
                active = is_active,
                fs_uniquifier=str(uuid.uuid4())
            )
            db.session.add(admin)
            db.session.flush()
        
        existing_role1 = Role.query.filter((Role.id == 2000) & (Role.name == "admin")).first()
        existing_role2 = Role.query.filter((Role.id == 2001) & (Role.name == "user")).first()
        # Role Initialization
        if existing_role1 and existing_role2:
            print(">> Roles already initialized.\n")
        else:
            if not existing_role1:
                role1 = Role(
                    id = 2000,
                    name = "admin",
                    description = "Admin/Quiz Master, will perform CRUD operations on subject, chapters, quizzes and will manage all the other users.",
                )

                db.session.add(role1)
                db.session.flush()

            if not existing_role2:
                role2 = Role(
                    id = 2001,
                    name = "user",
                    description = "User, is able to choose the subject as well as the chapter name and can take a ongoing quiz, View their respective quiz scores and overall summary.",
                )

                db.session.add(role2)
                db.session.flush()
                
            print(">> Roles Initialized Successfully...")

        # Admin-Role initialization
        exist_role_admin = Roles_Users.query.filter((Roles_Users.user_id == 1000) & (Roles_Users.role_id == 2000)).first()
        if not exist_role_admin:
            db.session.add(Roles_Users(id=3000,user_id=1000,role_id=2000))
            db.session.flush()

    except:
        db.session.rollback()
        print("<!>- Admin and Role Initialization Failed -<!>")
    else:
        if flag == 0:
            db.session.commit()
            save_admin_credentials("./database/admin_credentials.txt", g_id, passwd, 1)
            print('>> Admin Initialized Successfully... \n>> Default Admin credentials saved successfully at "./database/admin_credentials.txt"\n')