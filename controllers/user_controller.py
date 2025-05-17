from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
import sys
import os
from datetime import datetime
from sqlalchemy import func
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.user import User
from models.subject import Subject
from models.quiz import Quiz
from models.question import Question
from models.score import Score
from extensions import db
from models.chapter import Chapter

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/dashboard')
@login_required
def dashboard():
    # Get available subjects for the user
    subjects = Subject.query.all()
    
    # Get user's recent quiz attempts
    recent_attempts = Score.query.filter_by(user_id=current_user.id).order_by(Score.timestamp.desc()).limit(5).all()
    
    return render_template('user/dashboard.html', 
                          subjects=subjects, 
                          recent_attempts=recent_attempts)


@user_bp.route('/subjects')
@login_required
def subjects():
    subjects = Subject.query.all()
    return render_template('user/subjects.html', subjects=subjects)


@user_bp.route('/subject/<int:subject_id>')
@login_required
def subject_detail(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    chapters = subject.chapters.all()
    return render_template('user/subject_detail.html', subject=subject, chapters=chapters)


@user_bp.route('/quizzes/<int:chapter_id>')
@login_required
def chapter_quizzes(chapter_id):
    quizzes = Quiz.query.filter_by(chapter_id=chapter_id, is_active=True).all()
    return render_template('user/quizzes.html', quizzes=quizzes)


@user_bp.route('/quiz/<int:quiz_id>')
@login_required
def quiz_detail(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    # Check if already attempted
    attempted = Score.query.filter_by(user_id=current_user.id, quiz_id=quiz_id).first() is not None
    return render_template('user/quiz_detail.html', quiz=quiz, attempted=attempted)


@user_bp.route('/start-quiz/<int:quiz_id>')
@login_required
def start_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    if not questions:
        flash('This quiz has no questions.', 'warning')
        return redirect(url_for('user.quiz_detail', quiz_id=quiz_id))
    
    # Store quiz info in session
    session['quiz_id'] = quiz_id
    session['start_time'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    session['time_limit'] = quiz.time_limit
    
    return redirect(url_for('user.take_quiz'))


@user_bp.route('/take-quiz', methods=['GET', 'POST'])
@login_required
def take_quiz():
    quiz_id = session.get('quiz_id')
    if not quiz_id:
        flash('No active quiz session found.', 'warning')
        return redirect(url_for('user.dashboard'))
    
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    if request.method == 'POST':
        # Calculate score
        score = 0
        total = len(questions)
        correct_answers = 0
        
        for question in questions:
            selected_answer = request.form.get(f'question_{question.id}')
            if selected_answer == question.correct_answer:
                score += question.mark
                correct_answers += 1
        
        # Save score record
        score_entry = Score(
            user_id=current_user.id,
            quiz_id=quiz_id,
            total_questions=total,
            total_scored=correct_answers
        )
        db.session.add(score_entry)
        db.session.commit()
        
        # Clear session
        session.pop('quiz_id', None)
        session.pop('start_time', None)
        session.pop('time_limit', None)
        
        # Redirect to results
        flash(f'Quiz completed! You scored {correct_answers} out of {total} questions.', 'success')
        return redirect(url_for('user.quiz_result', score_id=score_entry.id))
    
    return render_template('user/take_quiz.html', quiz=quiz, questions=questions)


@user_bp.route('/quiz-result/<int:score_id>')
@login_required
def quiz_result(score_id):
    score = Score.query.get_or_404(score_id)
    
    # Check if the score belongs to the current user
    if score.user_id != current_user.id:
        flash('You do not have permission to view this result.', 'danger')
        return redirect(url_for('user.dashboard'))
    
    quiz = Quiz.query.get(score.quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz.id).all()
    
    return render_template('user/quiz_result.html', score=score, quiz=quiz, questions=questions)


@user_bp.route('/history')
@login_required
def history():
    # Get all user's scores
    scores = Score.query.filter_by(user_id=current_user.id).order_by(Score.timestamp.desc()).all()
    
    # Calculate statistics for summary tables and charts
    
    # 1. Subject performance summary
    subject_performance = db.session.query(
        Subject.name.label('subject_name'),
        func.count(Score.id).label('attempts'),
        func.avg(Score.total_scored * 100 / Score.total_questions).label('avg_percentage')
    ).join(Chapter, Subject.id == Chapter.subject_id)\
     .join(Quiz, Chapter.id == Quiz.chapter_id)\
     .join(Score, Quiz.id == Score.quiz_id)\
     .filter(Score.user_id == current_user.id)\
     .group_by(Subject.name)\
     .all()
    
    # 2. Recent quizzes summary (already have scores ordered by timestamp)
    
    # 3. Performance over time (for line chart)
    # Get timestamps and scores for the chart
    timeline_data = []
    for score in scores:
        timeline_data.append({
            'date': score.timestamp.strftime('%Y-%m-%d'),
            'score_percentage': round((score.total_scored / score.total_questions) * 100, 1),
            'quiz_title': score.quiz.title
        })
    
    # 4. Quiz performance by chapter
    chapter_performance = db.session.query(
        Chapter.name.label('chapter_name'),
        Subject.name.label('subject_name'),
        func.count(Score.id).label('attempts'),
        func.avg(Score.total_scored * 100 / Score.total_questions).label('avg_percentage')
    ).join(Subject, Chapter.subject_id == Subject.id)\
     .join(Quiz, Chapter.id == Quiz.chapter_id)\
     .join(Score, Quiz.id == Score.quiz_id)\
     .filter(Score.user_id == current_user.id)\
     .group_by(Chapter.name, Subject.name)\
     .all()
    
    # 5. Overall statistics
    total_quizzes_taken = len(scores)
    if total_quizzes_taken > 0:
        overall_average = sum([(s.total_scored / s.total_questions) * 100 for s in scores]) / total_quizzes_taken
    else:
        overall_average = 0
        
    best_score = max([(s.total_scored / s.total_questions) * 100 for s in scores], default=0)
    
    # Prepare data for charts
    chart_data = {
        'subjects': [item.subject_name for item in subject_performance],
        'subject_averages': [round(item.avg_percentage, 1) for item in subject_performance],
        'subject_attempts': [item.attempts for item in subject_performance],
        'timeline_dates': [item['date'] for item in timeline_data],
        'timeline_scores': [item['score_percentage'] for item in timeline_data],
        'timeline_titles': [item['quiz_title'] for item in timeline_data],
    }
    
    return render_template('user/history.html', 
                          scores=scores,
                          subject_performance=subject_performance,
                          chapter_performance=chapter_performance,
                          total_quizzes_taken=total_quizzes_taken,
                          overall_average=overall_average,
                          best_score=best_score,
                          chart_data=chart_data)