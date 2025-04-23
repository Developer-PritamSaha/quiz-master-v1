import os
from flask import Flask
from application.config import LocalDevConfig
from application.db_base import db
from flask_security import Security, SQLAlchemySessionUserDatastore
from application.models.login_model import User, Role

import logging
logging.basicConfig(filename='app.log', level=logging.DEBUG, format=f'%(asctime)s - %(levelname)s - %(name)s : %(message)s')


app = None

def create_app():
    app = Flask(__name__, template_folder="templates")
    if os.getenv('ENV', "development") == "production":
      raise Exception("\n>> Currently no production config is setup.")
    else:
      print("\n>> Staring Local Development...")
      app.config.from_object(LocalDevConfig)
    db.init_app(app)
    app.app_context().push()
    user_datastore = SQLAlchemySessionUserDatastore(db.session, User, Role)
    security = Security(app, user_datastore)
    return app

app = create_app()

# Imports all the models and controllers so they are loaded 
from application.controllers.login_controller import *
from application.controllers.admin_controller import *
from application.controllers.user_controller import *
from application.controllers.quiz_api_controller import *

if __name__ == '__main__':
  
  flag = True
  # Create the database tables or schema if they do not exist
  try:
    with app.app_context():
        db.create_all()
    print(">> Database Initialized Successfully...")
  except:
    print("*>> Database Initialization failed..")
    flag = False

  # Initialize default roles and admin user if not already initialized
  if flag:
    from application.utils.role_admin_init import *
    initialize_role_admin()    

  # Run the Flask app
  port = 5000
  print(f"\n🚀 Quiz Master is running at: http://127.0.0.1:{port}/\n   (ctrl + c - to quit)\n")
  app.run(port=port)
