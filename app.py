from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, current_user
import os
from extensions import db, migrate
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Initialize Login Manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    from models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from controllers.auth_controller import auth_bp
    from controllers.admin_controller import admin_bp
    from controllers.user_controller import user_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)
    
    # Home route
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            if current_user.is_admin:
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('user.dashboard'))
        return render_template('index.html')
    
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
        
        # Create admin user if it doesn't exist
        from werkzeug.security import generate_password_hash
        from datetime import datetime
        
        admin = User.query.filter_by(username='admin@example.com').first()
        if not admin:
            admin = User(
                username='admin@example.com',
                password_hash=generate_password_hash('admin123'),
                full_name='Administrator',
                qualification='Admin',
                dob=datetime.strptime('1990-01-01', '%Y-%m-%d'),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created!")
        else:
            # Ensuring admin user has admin rights and correct password
            admin.is_admin = True
            admin.password_hash = generate_password_hash('admin123')
            db.session.commit()
            print("Admin user updated!")
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)