from flask import jsonify
from flask import current_app as app
from application.models.quiz_model import *
from datetime import datetime

app.json.sort_keys = False

@app.route('/api/available/quizzes', methods=['GET'])
def get_available_quizzes():
    try:
        current_date = datetime.now().date()
        available_quizzes = []
        quiz_count = 0
        
        for q in Quiz.query.all():
            if(current_date >= q.date_of_quiz):
                temp = {
                    "quiz_id": q.id,
                    "subject_name": Subjects.query.filter_by(id=q.subject_id).first().name,
                    "chapter_name": Chapters.query.filter_by(id=q.chapter_id).first().name,
                    "no_of_questions": Questions.query.filter_by(quiz_id=q.id).count(),
                    "total_marks": q.total_marks,
                    "date_of_quiz": q.date_of_quiz.strftime("%Y-%m-%d"),
                    "duration_in_sec": (q.time_duration.hour * 60 + q.time_duration.minute) * 60 + q.time_duration.second 
                }
                quiz_count += 1
                available_quizzes += [temp]
  
        if quiz_count > 0:
            return jsonify(available_quizzes)
        else:
            return "", 204
    except Exception:
        app.logger.exception("<!> API Error in '/api/available/quizzes' | Method : 'GET'")
        return "", 500
    
@app.route('/api/quiz/<int:quiz_id>/questions', methods=['GET'])
def get_quiz_questions(quiz_id):
    try:
        current_date = datetime.now().date()
        available_questions = []
        question_count = 0
        quiz_exist = Quiz.query.filter_by(id=quiz_id).first()
        
        if quiz_exist and (current_date >= quiz_exist.date_of_quiz):
            for qu in Questions.query.filter_by(quiz_id=quiz_id).all():
                temp = {
                    "question_id": qu.id,
                    "type": qu.question_type,
                    "marks": qu.marks,
                    "title": qu.question_title,
                    "statement": qu.question_statement,
                    "options": [op.option_statement for op in Options.query.filter_by(question_id=qu.id).all()],
                    "correct_option": qu.correct_option
                }
                question_count += 1
                available_questions += [temp]
    
            if question_count > 0:
                return jsonify(available_questions)
            else:
                return "", 204
        else:
            return "", 404
    except:
        app.logger.exception("<!> API Error in '/api/quiz/<int:quiz_id>/questions' | Method : 'GET'")
        return "", 500