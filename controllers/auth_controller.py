from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.user import User
from extensions import db
from forms.auth import LoginForm, RegisterForm
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        print(f"User already authenticated: {current_user.username}, admin: {current_user.is_admin}")
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('user.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        print(f"Login attempt with email: {form.email.data}")
        user = User.query.filter_by(username=form.email.data).first()
        
        if user:
            print(f"User found: {user.username}, Admin: {user.is_admin}")
            if user.verify_password(form.password.data):
                print(f"Password verified for {user.username}")
                login_user(user)
                print(f"User logged in: {current_user.username}, Admin: {current_user.is_admin}")
                
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                elif user.is_admin:
                    print(f"Redirecting admin to dashboard")
                    return redirect(url_for('admin.dashboard'))
                else:
                    print(f"Redirecting user to dashboard")
                    return redirect(url_for('user.dashboard'))
            else:
                print(f"Password verification failed for {user.username}")
                flash('Invalid email or password', 'danger')
        else:
            print(f"No user found with email: {form.email.data}")
            flash('Invalid email or password', 'danger')
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('user.dashboard'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            user = User(
                username=form.email.data,
                full_name=form.full_name.data,
                qualification=form.qualification.data,
                dob=form.dob.data,
                is_admin=False
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            print(f"Registration error: {str(e)}")
            flash('Error during registration. Please try again.', 'danger')
    
    return render_template('auth/register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = RegisterForm(obj=current_user)
    
    # Explicitly set email field to match the username from the model
    form.email.data = current_user.username
    
    if request.method == 'GET':
        # Don't prefill password fields
        form.password.data = ''
        form.confirm_password.data = ''
    
    if form.validate_on_submit():
        current_user.full_name = form.full_name.data
        current_user.qualification = form.qualification.data
        current_user.dob = form.dob.data
        
        if form.password.data:
            current_user.set_password(form.password.data)
            
        try:
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('auth.profile'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile. {str(e)}', 'danger')
    
    return render_template('auth/profile.html', form=form)