from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.user import User
from models.subject import Subject
from models.chapter import Chapter
from models.quiz import Quiz
from models.question import Question
from models.score import Score
from forms.admin import SubjectForm, ChapterForm, QuizForm, QuestionForm, UserForm
from forms.admin_search import SearchForm
from extensions import db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    # Check if the user is admin
    if not current_user.is_admin:
        flash('You do not have permission to access the admin dashboard.', 'danger')
        return redirect(url_for('user.dashboard'))
    
    # Get dashboard statistics
    user_count = User.query.filter_by(is_admin=False).count()
    subject_count = Subject.query.count()
    quiz_count = Quiz.query.count()
    attempt_count = Score.query.count()
    
    # Get recent quiz activities
    recent_activities = Score.query.order_by(Score.timestamp.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                          user_count=user_count,
                          subject_count=subject_count,
                          quiz_count=quiz_count,
                          attempt_count=attempt_count,
                          recent_activities=recent_activities if recent_activities else [])

@admin_bp.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('user.dashboard'))
    
    form = SearchForm()
    results = []
    search_type = 'user'  # Default search type
    
    if form.validate_on_submit() or request.args.get('query'):
        # Get search parameters from form or URL
        query = form.search_query.data if form.validate_on_submit() else request.args.get('query', '')
        search_type = form.search_type.data if form.validate_on_submit() else request.args.get('type', 'user')
        
        # Perform search based on type
        if search_type == 'user':
            results = User.query.filter(
                db.or_(
                    User.username.ilike(f'%{query}%'),
                    User.full_name.ilike(f'%{query}%'),
                    User.qualification.ilike(f'%{query}%')
                )
            ).all()
        elif search_type == 'subject':
            results = Subject.query.filter(
                db.or_(
                    Subject.name.ilike(f'%{query}%'),
                    Subject.description.ilike(f'%{query}%')
                )
            ).all()
        elif search_type == 'quiz':
            results = Quiz.query.join(Chapter).join(Subject).filter(
                db.or_(
                    Quiz.title.ilike(f'%{query}%'),
                    Quiz.description.ilike(f'%{query}%'),
                    Chapter.name.ilike(f'%{query}%'),
                    Subject.name.ilike(f'%{query}%')
                )
            ).all()
    
    return render_template('admin/search_results.html', 
                           form=form, 
                           results=results, 
                           search_type=search_type,
                           query=query if 'query' in locals() else '')
    
# Subject Management
@admin_bp.route('/subjects')
@login_required
def subjects():
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('user.dashboard'))
    
    subjects = Subject.query.all()
    return render_template('admin/subjects.html', subjects=subjects)


@admin_bp.route('/add-subject', methods=['GET', 'POST'])
@login_required
def add_subject():
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('user.dashboard'))
    
    form = SubjectForm()
    if form.validate_on_submit():
        subject = Subject(
            name=form.name.data,
            description=form.description.data
        )
        db.session.add(subject)
        db.session.commit()
        flash('Subject added successfully!', 'success')
        return redirect(url_for('admin.subjects'))
    
    return render_template('admin/add_subject.html', form=form)


@admin_bp.route('/edit-subject/<int:subject_id>', methods=['GET', 'POST'])
@login_required
def edit_subject(subject_id):
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('user.dashboard'))
    
    subject = Subject.query.get_or_404(subject_id)
    form = SubjectForm(obj=subject)
    if form.validate_on_submit():
        subject.name = form.name.data
        subject.description = form.description.data
        db.session.commit()
        flash('Subject updated successfully!', 'success')
        return redirect(url_for('admin.subjects'))
    
    return render_template('admin/edit_subject.html', form=form, subject=subject)


@admin_bp.route('/delete-subject/<int:subject_id>', methods=['POST'])
@login_required
def delete_subject(subject_id):
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('user.dashboard'))
    
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    flash('Subject deleted successfully!', 'success')
    return redirect(url_for('admin.subjects'))


# Chapter Management
@admin_bp.route('/chapters/<int:subject_id>')
@login_required
def chapters(subject_id):
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('user.dashboard'))
    
    subject = Subject.query.get_or_404(subject_id)
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    return render_template('admin/chapters.html', subject=subject, chapters=chapters)


@admin_bp.route('/add-chapter', methods=['GET', 'POST'])
@login_required
def add_chapter():
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('user.dashboard'))
    
    form = ChapterForm()
    form.subject_id.choices = [(s.id, s.name) for s in Subject.query.all()]
    
    if form.validate_on_submit():
        chapter = Chapter(
            name=form.name.data,
            description=form.description.data,
            subject_id=form.subject_id.data
        )
        db.session.add(chapter)
        db.session.commit()
        flash('Chapter added successfully!', 'success')
        return redirect(url_for('admin.chapters', subject_id=form.subject_id.data))
    
    return render_template('admin/add_chapter.html', form=form)


@admin_bp.route('/edit-chapter/<int:chapter_id>', methods=['GET', 'POST'])
@login_required
def edit_chapter(chapter_id):
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('user.dashboard'))
    
    chapter = Chapter.query.get_or_404(chapter_id)
    form = ChapterForm(obj=chapter)
    form.subject_id.choices = [(s.id, s.name) for s in Subject.query.all()]
    
    if form.validate_on_submit():
        chapter.name = form.name.data
        chapter.description = form.description.data
        chapter.subject_id = form.subject_id.data
        db.session.commit()
        flash('Chapter updated successfully!', 'success')
        return redirect(url_for('admin.chapters', subject_id=chapter.subject_id))
    
    return render_template('admin/edit_chapter.html', form=form, chapter=chapter)


@admin_bp.route('/delete-chapter/<int:chapter_id>', methods=['POST'])
@login_required
def delete_chapter(chapter_id):
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('user.dashboard'))
    
    chapter = Chapter.query.get_or_404(chapter_id)
    subject_id = chapter.subject_id
    db.session.delete(chapter)
    db.session.commit()
    flash('Chapter deleted successfully!', 'success')
    return redirect(url_for('admin.chapters', subject_id=subject_id))


# Quiz Management
@admin_bp.route('/quizzes')
@login_required
def quizzes():
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('user.dashboard'))
    
    quizzes = Quiz.query.all()
    return render_template('admin/quizzes.html', quizzes=quizzes)


@admin_bp.route('/create-quiz', methods=['GET', 'POST'])
@login_required
def create_quiz():
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('user.dashboard'))
    
    form = QuizForm()
    chapters = Chapter.query.join(Subject).all()
    form.chapter_id.choices = [(c.id, f"{c.subject.name} - {c.name}") for c in chapters] if chapters else []
    
    if form.validate_on_submit():
        quiz = Quiz(
            title=form.title.data,
            description=form.description.data,
            time_limit=form.time_limit.data,
            chapter_id=form.chapter_id.data,
            is_active=form.is_active.data
        )
        db.session.add(quiz)
        db.session.commit()
        flash('Quiz created successfully! Add questions now.', 'success')
        return redirect(url_for('admin.edit_quiz', quiz_id=quiz.id))
    
    return render_template('admin/create_quiz.html', form=form)


@admin_bp.route('/edit-quiz/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def edit_quiz(quiz_id):
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('user.dashboard'))
    
    quiz = Quiz.query.get_or_404(quiz_id)
    form = QuizForm(obj=quiz)
    chapters = Chapter.query.join(Subject).all()
    form.chapter_id.choices = [(c.id, f"{c.subject.name} - {c.name}") for c in chapters] if chapters else []
    
    if form.validate_on_submit():
        quiz.title = form.title.data
        quiz.description = form.description.data
        quiz.time_limit = form.time_limit.data
        quiz.chapter_id = form.chapter_id.data
        quiz.is_active = form.is_active.data
        db.session.commit()
        flash('Quiz updated successfully!', 'success')
        return redirect(url_for('admin.quizzes'))
    
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    return render_template('admin/edit_quiz.html', form=form, quiz=quiz, questions=questions)


@admin_bp.route('/delete-quiz/<int:quiz_id>', methods=['POST'])
@login_required
def delete_quiz(quiz_id):
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('user.dashboard'))
    
    quiz = Quiz.query.get_or_404(quiz_id)
    db.session.delete(quiz)
    db.session.commit()
    flash('Quiz deleted successfully!', 'success')
    return redirect(url_for('admin.quizzes'))


# Question Management
@admin_bp.route('/add-question/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def add_question(quiz_id):
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('user.dashboard'))
    
    quiz = Quiz.query.get_or_404(quiz_id)
    form = QuestionForm()
    
    if form.validate_on_submit():
        question = Question(
            quiz_id=quiz_id,
            question_text=form.question_text.data,
            option1=form.option1.data,
            option2=form.option2.data,
            option3=form.option3.data,
            option4=form.option4.data,
            correct_answer=form.correct_answer.data,
            mark=form.mark.data
        )
        db.session.add(question)
        db.session.commit()
        flash('Question added successfully!', 'success')
        if 'add_another' in request.form:
            return redirect(url_for('admin.add_question', quiz_id=quiz_id))
        else:
            return redirect(url_for('admin.edit_quiz', quiz_id=quiz_id))
    
    return render_template('admin/add_question.html', form=form, quiz=quiz)


@admin_bp.route('/edit-question/<int:question_id>', methods=['GET', 'POST'])
@login_required
def edit_question(question_id):
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('user.dashboard'))
    
    question = Question.query.get_or_404(question_id)
    form = QuestionForm(obj=question)
    
    if form.validate_on_submit():
        question.question_text = form.question_text.data
        question.option1 = form.option1.data
        question.option2 = form.option2.data
        question.option3 = form.option3.data
        question.option4 = form.option4.data
        question.correct_answer = form.correct_answer.data
        question.mark = form.mark.data
        db.session.commit()
        flash('Question updated successfully!', 'success')
        return redirect(url_for('admin.edit_quiz', quiz_id=question.quiz_id))
    
    return render_template('admin/edit_question.html', form=form, question=question)


@admin_bp.route('/delete-question/<int:question_id>', methods=['POST'])
@login_required
def delete_question(question_id):
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('user.dashboard'))
    
    question = Question.query.get_or_404(question_id)
    quiz_id = question.quiz_id
    db.session.delete(question)
    db.session.commit()
    flash('Question deleted successfully!', 'success')
    return redirect(url_for('admin.edit_quiz', quiz_id=quiz_id))


# User Management
@admin_bp.route('/users')
@login_required
def users():
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('user.dashboard'))
    
    users = User.query.all()
    return render_template('admin/users.html', users=users)


@admin_bp.route('/user/<int:user_id>')
@login_required
def user_detail(user_id):
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('user.dashboard'))
    
    user = User.query.get_or_404(user_id)
    scores = Score.query.filter_by(user_id=user_id).order_by(Score.timestamp.desc()).all()
    return render_template('admin/user_detail.html', user=user, scores=scores)


@admin_bp.route('/edit-user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('user.dashboard'))
    
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.full_name = form.full_name.data
        user.qualification = form.qualification.data
        user.is_admin = form.is_admin.data
        
        if form.password.data:
            user.password_hash = generate_password_hash(form.password.data)
            
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/edit_user.html', form=form, user=user)


@admin_bp.route('/toggle-user-status/<int:user_id>', methods=['POST'])
@login_required
def toggle_user_status(user_id):
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('user.dashboard'))
    
    user = User.query.get_or_404(user_id)
    # Don't allow deactivating your own admin account
    if user.id == current_user.id and user.is_admin:
        flash('You cannot deactivate your own admin account!', 'danger')
        return redirect(url_for('admin.users'))
    
    user.is_active = not user.is_active
    db.session.commit()
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.username} has been {status}!', 'success')
    return redirect(url_for('admin.users'))


# Reports
@admin_bp.route('/reports')
@login_required
def reports():
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('user.dashboard'))
    
    # Basic statistics
    total_users = User.query.filter_by(is_admin=False).count()
    active_quizzes = Quiz.query.filter_by(is_active=True).count()
    total_attempts = Score.query.count()
    
    # Get attempts per subject
    subject_stats = db.session.query(
        Subject.name,
        db.func.count(Score.id).label('attempts'),
        db.func.avg((Score.total_scored * 100) / Score.total_questions).label('avg_score')
    ).join(Chapter, Subject.id == Chapter.subject_id)\
     .join(Quiz, Chapter.id == Quiz.chapter_id)\
     .join(Score, Quiz.id == Score.quiz_id)\
     .group_by(Subject.name)\
     .all()
    
    # Recent attempts
    recent_attempts = Score.query.order_by(Score.timestamp.desc()).limit(20).all()
    
    return render_template('admin/reports.html', 
                          total_users=total_users,
                          active_quizzes=active_quizzes,
                          total_attempts=total_attempts,
                          subject_stats=subject_stats,
                          recent_attempts=recent_attempts)


@admin_bp.route('/export-report/<report_type>')
@login_required
def export_report(report_type):
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('user.dashboard'))
    
    if report_type == 'users':
        users = User.query.filter_by(is_admin=False).all()
        data = [{
            'id': user.id,
            'username': user.username,
            'full_name': user.full_name,
            'qualification': user.qualification,
            'created_at': user.created_at.strftime('%Y-%m-%d')
        } for user in users]
        return jsonify(data)
    
    elif report_type == 'scores':
        scores = Score.query.all()
        data = [{
            'id': score.id,
            'user': score.user.full_name,
            'quiz': score.quiz.title,
            'scored': score.total_scored,
            'total': score.total_questions,
            'percentage': (score.total_scored / score.total_questions) * 100,
            'timestamp': score.timestamp.strftime('%Y-%m-%d %H:%M')
        } for score in scores]
        return jsonify(data)
    
    else:
        flash('Invalid report type', 'danger')
        return redirect(url_for('admin.reports'))