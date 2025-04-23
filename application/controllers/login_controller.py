from flask import request, redirect
from flask import render_template
from flask import current_app as app
from flask_security.utils import hash_password
from flask_security.decorators import login_required
from flask_login import login_user, logout_user, current_user
from application.models.login_model import *
from application.utils.user_auth import authenticate_user, valid_email
from application.utils.integrity_checker import check_db_integrity
from ..db_base import db
from datetime import datetime
import uuid

@app.route("/", methods=["GET", "POST"])
def home():
    try:
        if not check_db_integrity():
            raise Exception("<!>---Database integrity error---<!>")
        else:
            username = ""
            f = 0
            if current_user.is_authenticated:
                u_id = current_user.id
                if u_id == 1000:
                    username = "Quiz Master"
                elif u_id != 1000:
                    username = User_Data.query.filter_by(user_id=u_id).first().full_name
                f=1
            return render_template("home.html", flag=f, u_name=username) 
    except Exception:
        app.logger.exception('<!> Home Error')
        return render_template("server_error.html"),500 
        
@app.route("/login", methods=["GET","POST"])
def login():
    try:
        if not check_db_integrity():
            raise Exception("<!>---Database integrity error---<!>")
        else:
            if current_user.is_authenticated:
                return redirect("/loggedin")
            
            if request.method == 'GET':
                return render_template("security/login.html", flag=0) 
            
            elif request.method == 'POST':
                email = request.form["email"].strip()
                password = request.form["passwd"]
                remember = True if request.form.get("remember") else False 

                user = authenticate_user(email,password)
                if user[0]:
                    login_user(user[1], remember=remember)
                    u_id = current_user.id
                    if u_id == 1000:
                        username = "Quiz Master"
                    elif u_id != 1000:
                        username = User_Data.query.filter_by(user_id=u_id).first().full_name  
                    app.logger.info(f">> Login : User_id - {current_user.id}, Username - {username}")
                    return redirect("/loggedin")
                else:
                    app.logger.warning("<!> Login-Error: Invalid Email or Password.")
                    return render_template("security/login.html", flag=1, e=email) 

            else:
                app.logger.warning("<---- Bad Request to '/login' ---->")
                return render_template("server_error.html"),500 
            
    except Exception:
        app.logger.exception('<!> Login Error')
        return render_template("server_error.html"),500 

@app.route("/loggedin")
@login_required
def check_roles():
    if not check_db_integrity():
        app.logger.error("<!>--- Database integrity error. Logging out existing user ---<!>")
        return redirect("/logout")
    if "admin" in [role.name for role in current_user.roles]:
        return redirect("/admin")
    elif "user" in [role.name for role in current_user.roles]:
        return redirect("/user")
    else:
        return redirect("/")
    
@app.route("/logout")
@login_required
def logout():
    u_id = current_user.id
    if u_id == 1000:
        username = "Quiz Master"
    elif u_id != 1000:
        username = User_Data.query.filter_by(user_id=u_id).first().full_name  
    app.logger.info(f">> Logout : User_id - {current_user.id}, Username - {username}")
    logout_user()  
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    try:
        if not check_db_integrity():
            raise Exception("<!>---Database integrity error---<!>")
        else:
            if request.method == "GET":
                return render_template("security/register.html",invalid_email = 0, email_exist = 0, invalid_passwd = 0, name_empty = 0, invalid_format = 0, dob_false = 0)
            
            elif request.method == "POST":
                email = request.form["email"].strip().lower()
                passwd = request.form["passwd"].strip()
                name = request.form["full_name"].strip()
                doc = request.files["doc"]
                dob_string = request.form["dob"]

                data_valid = True

                # Data Validation
                invalid_email, email_exist, invalid_passwd, name_empty, invalid_format, dob_false = 0, 0, 0, 0, 0, 0
                # validate email address
                if not valid_email(email)[0]:
                    invalid_email = 1
                    data_valid = False
                    app.logger.warning("<!> SignUp-Error: Invalid Email address")
                if User.query.filter_by(email=email).first():
                    email_exist = 1
                    data_valid = False
                    app.logger.warning("<!> SignUp-Error: Email already exist")
                if (passwd == "") or (len(passwd) < 8) or (" " in passwd):
                    invalid_passwd = 1
                    data_valid = False
                    app.logger.warning("<!> SignUp-Error: Invalid Password")
                if name == "":
                    name_empty = 1
                    data_valid = False
                    app.logger.warning("<!> SignUp-Error: Name field is empty")
                t = len(doc.filename)
                if (t < 5) or (doc.filename[t-4:].lower() not in ['.pdf','.png','.jpg']):
                    invalid_format = 1
                    data_valid = False
                    app.logger.warning("<!> SignUp-Error: Invalid file format")
                # Converts string to datetime.date or Python date object
                dob = datetime.strptime(dob_string, "%Y-%m-%d").date()
                current_date = datetime.now().date()
                age = current_date.year - dob.year
                if age < 5:
                    dob_false = 1
                    data_valid = False
                    app.logger.warning("<!> SignUp-Error: Invalid D.O.B")

                if not data_valid:
                    return render_template("security/register.html",invalid_email = invalid_email, email_exist = email_exist, invalid_passwd=invalid_passwd, name_empty = name_empty, invalid_format = invalid_format, dob_false = dob_false, e=email, n=name, d=dob_string) 
                
                else:
                    try:
                        new_login_details = User(
                            email = email,
                            password = hash_password(passwd),
                            active = True,
                            fs_uniquifier=str(uuid.uuid4())
                        )
                        db.session.add(new_login_details)
                        db.session.flush()

                        if User_Data.query.count() == 0:
                            new_registration = User_Data(
                            id = 4000,
                            user_id = new_login_details.id,
                            full_name=name,
                            qualification=doc.read(),
                            dob=dob)
                            
                        else:
                            new_registration = User_Data(
                            user_id = new_login_details.id,
                            full_name=name,
                            qualification=doc.read(),
                            dob=dob)
                        
                        db.session.add(new_registration)
                        db.session.flush()

                        db.session.add(Roles_Users(user_id=new_login_details.id,role_id=2001))

                    except Exception:
                        db.session.rollback()
                        app.logger.exception("<!> Rolling back new registration commit due to an issue.")
                    else:
                        db.session.commit()

                return redirect("/login")

            else:
                app.logger.warning("<-----  Bad Request to '/register' ----->")
                return render_template("server_error.html"),500 
            
    except Exception:
        app.logger.exception('<!> Registration Error')
        return render_template("server_error.html"),500 
    