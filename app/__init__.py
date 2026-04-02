from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # 🔐 SECRET KEY - Use environment variable for security
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "pigpeople_secret")
    
    # ✅ DATABASE CONFIGURATION - NOW WORKS WITH POSTGRESQL
    database_url = os.environ.get("DATABASE_URL")
    
    if database_url:
        # Fix for Render's PostgreSQL URL
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
        print(f"✅ Using PostgreSQL database")
    else:
        # Local development with SQLite
        BASE_DIR = os.path.abspath(os.path.dirname(__file__))
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "pigpeople.db")
        print(f"⚠️ Using SQLite (local only)")
    
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    db.init_app(app)
    
    # 🔐 LOGIN SETUP
    login_manager.login_view = "main.login"
    login_manager.init_app(app)
    
    from .models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # 📦 REGISTER ROUTES
    from .routes import main
    app.register_blueprint(main)
    
    # 🧠 CREATE DB + DEFAULT ADMIN
    with app.app_context():
        db.create_all()
        from werkzeug.security import generate_password_hash
        
        # 🔍 Check if admin already exists
        existing_admin = User.query.filter_by(username="masuwa_chikonkolo").first()
        if not existing_admin:
            admin = User(
                name="Masuwa Chikonkolo",
                username="masuwa_chikonkolo",
                password=generate_password_hash("chikonkz999"),
                role="admin"
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Default admin created!")
        else:
            print(f"✅ Admin already exists - Database has {User.query.count()} users")
    
    return app
