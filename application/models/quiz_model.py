from ..db_base import db

class Subjects(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.String, nullable=False)
    chapters = db.relationship('Chapters', backref='subjects', cascade="all, delete-orphan")
    quizzes = db.relationship('Quiz', backref='subjects', cascade="all, delete-orphan")

class Chapters(db.Model):
    __tablename__ = 'chapters'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    name = db.Column(db.String, nullable=False)
    no_questions = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String, nullable=False)
    quizzes = db.relationship('Quiz', backref='chapters', cascade="all, delete-orphan")

class Quiz(db.Model):
    __tablename__ = 'quiz'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False)
    date_of_quiz = db.Column(db.Date, nullable=False)
    time_duration = db.Column(db.Time, nullable=False)
    total_marks = db.Column(db.Integer, nullable=False)
    remarks = db.Column(db.Integer, nullable=False) 
    questions = db.relationship('Questions', backref='quiz', cascade="all, delete-orphan")
    scores = db.relationship('Scores', backref='quiz', cascade="all, delete-orphan")

class Questions(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.id", ondelete="CASCADE"), nullable=False)
    marks = db.Column(db.Integer, nullable=False)
    question_title = db.Column(db.String, nullable=False)
    question_statement = db.Column(db.String, nullable=False)
    question_type = db.Column(db.String, nullable=False)
    correct_option = db.Column(db.Integer, nullable=False)
    options = db.relationship('Options', backref='questions', cascade="all, delete-orphan")

class Options(db.Model):
    __tablename__ = 'options'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    option_no = db.Column(db.Integer, nullable=False)
    option_statement = db.Column(db.String, nullable=False)
    
class Scores(db.Model):
    __tablename__ = 'scores'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.id", ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    question_attempted = db.Column(db.Integer, nullable=False)
    answered_correct = db.Column(db.Integer, nullable=False)
    attempt_date = db.Column(db.Date, nullable=False)
    attempt_time = db.Column(db.Time, nullable=False)
    time_taken = db.Column(db.String, nullable=False)
    total_scored = db.Column(db.Integer, nullable=False)
