from extensions import db
from datetime import datetime

class Score(db.Model):
    __tablename__ = 'scores'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    total_scored = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Methods
    def get_percentage(self):
        if self.total_questions > 0:
            return (self.total_scored / self.total_questions) * 100
        return 0