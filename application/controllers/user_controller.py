from flask import request, redirect
from flask import render_template
from flask import current_app as app
from flask_login import current_user
from flask_security.decorators import login_required, roles_required
from application.models.quiz_model import *
from application.models.login_model import User_Data
from datetime import datetime as dt
from math import floor, ceil
from ..db_base import db


@app.route("/user", methods=["GET", "POST"])
@login_required
@roles_required("user")
def user():
    try:
        quiz = Quiz.query.all()
        sub_name = {} # key: chapter_id, value: subject_name
        chap_name = {} # key: chapter_id, value: chapter_name
        ques = {} # key: quiz_id, value: count of associated questions
        quiz_date = {} # key: quiz_id, value: quiz_date
        for q in quiz:
            quiz_date[q.id] = q.date_of_quiz.strftime("%d-%m-%Y")
            ques[q.id] = Questions.query.filter_by(quiz_id=q.id).count()
            if q.chapter_id not in sub_name:
                temp = Chapters.query.filter_by(id=q.chapter_id).first()
                sub_name[q.chapter_id] = Subjects.query.filter_by(id=temp.subject_id).first().name
                chap_name[q.chapter_id] = temp.name
            if q.chapter_id not in chap_name:
                chap_name[q.chapter_id] = Chapters.query.filter_by(id=q.chapter_id).first().name

        username = "Guest"
        if current_user.is_authenticated:
            u_id = current_user.id 
            username = User_Data.query.filter_by(user_id=u_id).first().full_name

        return render_template("user_dashboard.html",quizzes=quiz,q_date=quiz_date,no_questions=ques,sub_name=sub_name,chap_name=chap_name,u_name=username, search_val="", search_flag=0) 
    
    except Exception:
        app.logger.warning("<!>-- Quiz loading failed --<!>")
        app.logger.exception('<!> User Dashboard Error')
        return render_template("server_error.html"),500

@app.route("/user/search/quiz", methods=["GET"])
@login_required
@roles_required("user")
def search_quizzes():
    try:
        search_str = request.args.get("query_str", "").strip()  
        if(search_str == ""):
            return redirect("/user")
        else:
            quiz = []
            sub_name = {} 
            chap_name = {} 
            ques = {}
            quiz_date = {}
            username = "Guest"
            if current_user.is_authenticated:
                u_id = current_user.id 
                username = User_Data.query.filter_by(user_id=u_id).first().full_name

            # Filter quizzes
            if search_str.isdigit(): # filter by quiz id
                quiz = Quiz.query.filter_by(id=int(search_str)).all()

            elif(Subjects.query.filter(Subjects.name.like(f"%{search_str}%")).first()): # filter by subject
                temp_sub = Subjects.query.filter(Subjects.name.like(f"%{search_str}%")).all()
                for sub in temp_sub:
                    quiz += Quiz.query.filter_by(subject_id=sub.id).all()
                
            elif(Chapters.query.filter(Chapters.name.like(f"%{search_str}%")).first()): # filter by chapter
                temp_chap = Chapters.query.filter(Chapters.name.like(f"%{search_str}%")).all()
                for chap in temp_chap:
                    quiz += Quiz.query.filter_by(chapter_id=chap.id).all()
            
            else: # filter by date of quiz
                try:
                    search_date = dt.strptime(search_str, "%d-%m-%Y").date() 
                    quiz = Quiz.query.filter_by(date_of_quiz=search_date).all()
                    
                except: # if the date format has any error then no result
                    return render_template("user_dashboard.html",quizzes=[],q_date=quiz_date,no_questions=ques,sub_name=sub_name,chap_name=chap_name,u_name=username, search_val=search_str, search_flag=1)
                
            for q in quiz:
                quiz_date[q.id] = q.date_of_quiz.strftime("%d-%m-%Y")
                ques[q.id] = Questions.query.filter_by(quiz_id=q.id).count()
                if q.chapter_id not in sub_name:
                    temp = Chapters.query.filter_by(id=q.chapter_id).first()
                    sub_name[q.chapter_id] = Subjects.query.filter_by(id=temp.subject_id).first().name
                    chap_name[q.chapter_id] = temp.name
                if q.chapter_id not in chap_name:
                    chap_name[q.chapter_id] = Chapters.query.filter_by(id=q.chapter_id).first().name

            return render_template("user_dashboard.html",quizzes=quiz,q_date=quiz_date,no_questions=ques,sub_name=sub_name,chap_name=chap_name,u_name=username, search_val=search_str, search_flag=1) 
    
    except Exception:
        app.logger.exception('<!> User Quiz Search Error')
        return render_template("server_error.html"),500
    
@app.route("/start/quiz/<int:quiz_id>", methods=["GET", "POST"])
@login_required
@roles_required("user")
def start_quiz(quiz_id):
    try:
        username = "Guest"
        if current_user.is_authenticated:
            u_id = current_user.id 
            username = User_Data.query.filter_by(user_id=u_id).first().full_name

        quiz = Quiz.query.filter_by(id=quiz_id).first()
        quiz_available = 0
        current_date = dt.now().date()
        if(current_date >= quiz.date_of_quiz):
            quiz_available = 1

        if (quiz_available == 1):
            chap_name = Chapters.query.filter_by(id=quiz.chapter_id).first().name
            quiz_name = "Quiz" + "-" + chap_name + "-" + str(quiz.id)
            ques = Questions.query.filter_by(quiz_id=quiz_id).all()
            opts = {} # key: question_id, value: list of options
            temp = quiz.time_duration    
            quiz_duration = (temp.hour * 60 + temp.minute) * 60 + temp.second # in seconds
            for q in ques:
                opts[q.id] = Options.query.filter_by(question_id=q.id).all()

            atmpt_date = dt.now().strftime("%Y-%m-%d")
            atmpt_time = dt.now().strftime("%H:%M:%S")

            return render_template("quiz_dashboard.html",quiz_avilable=quiz_available,quiz=quiz,questions=ques,options=opts,quiz_name=quiz_name,u_name=username,attempt_date=atmpt_date,attempt_time=atmpt_time,quiz_duration=quiz_duration) 
        
        else:
            return render_template("quiz_dashboard.html",quiz_available=quiz_available,questions=[],attempt_id=(-1),u_name=username)
        
    except Exception:
        app.logger.exception(f'<!> User Quiz Start Error for, Quiz ID: {quiz_id}')
        db.session.rollback()
        return render_template("server_error.html"),500 
    
@app.route("/user/quiz/submit/<int:quiz_id>", methods=["POST"])
@login_required
@roles_required("user")
def evaluate_score(quiz_id):
    if request.method == "POST":
        try:
            questions = Questions.query.filter_by(quiz_id=quiz_id).all()
            unattempted_count = 0
            correct_count = 0
            total_marks = 0
            for q in questions:
                temp_option = int(request.form.get(str(q.id)+"_option","0"))
                if temp_option == q.correct_option:
                    total_marks += q.marks
                    correct_count += 1
                elif temp_option == 0:
                    unattempted_count += 1

            time_taken = int(request.form["complete_time"]) # in seconds

            if time_taken < 0:
                time_taken_str = "Invalid"
            else:
                # Extract hours, minutes and seconds from time_taken
                hours = floor(time_taken / 3600)
                minutes = floor((time_taken % 3600) / 60)
                seconds = time_taken % 60
                time_taken_str = f'{hours} hr. {minutes} m {seconds} s'

            # Looging the quiz attempt
            new_attempt = Scores(
                quiz_id=quiz_id,
                user_id = current_user.id,
                question_attempted = len(questions) - unattempted_count,
                answered_correct = correct_count,
                attempt_date = dt.strptime(request.form["attempt_date"], "%Y-%m-%d").date(),
                attempt_time = dt.strptime(request.form["attempt_time"], "%H:%M:%S").time(),
                time_taken = time_taken_str,
                total_scored = total_marks)
            
            db.session.add(new_attempt)
            db.session.flush()

        except Exception:
            db.session.rollback()
            app.logger.exception(f"<!> Rolling back Quiz Submission commits for, Quiz ID: {quiz_id}, due to some issue.")
            return render_template("alert.html",message="<!> Quiz submission unsuccessful.", redirect_after="/user/scores")
        else:
            db.session.commit()

        return redirect("/user/scores")
    
    else: 
        app.logger.warning("<--- Bad Request to '/user/quiz/submit/<int:quiz_id>' --->")
        return render_template("server_error.html"),500
    
@app.route("/user/scores", methods=["GET","POST"])
@login_required
@roles_required("user")
def user_scores():
    try:
        scores = Scores.query.filter_by(user_id=current_user.id).all()
        scores.reverse()
        quiz_marks = {} # key: score_id, value: quiz_marks
        sub_name = {} # key: score_id, value: subject_name
        chap_name = {} # key: score_id, value: chapter_name
        no_ques = {} # key: score_id, value: count of associated questions
        timestamp = {} # key: score_id, value: [<attempt_date>,<attempt_time>]

        for s in scores:
            q = Quiz.query.filter_by(id=s.quiz_id).first()
            timestamp[s.id] = [s.attempt_date.strftime("%d-%m-%Y"), s.attempt_time.strftime("%H:%M:%S") ]
            quiz_marks[s.id] = q.total_marks
            no_ques[s.id] = Questions.query.filter_by(quiz_id=q.id).count()
            if s.id not in sub_name:
                temp = Chapters.query.filter_by(id=q.chapter_id).first()
                sub_name[s.id] = Subjects.query.filter_by(id=temp.subject_id).first().name
                chap_name[s.id] = temp.name
            if s.id not in chap_name:
                chap_name[s.id] = Chapters.query.filter_by(id=q.chapter_id).first().name

        username = "Guest"
        if current_user.is_authenticated:
            u_id = current_user.id 
            username = User_Data.query.filter_by(user_id=u_id).first().full_name

        return render_template("user_score_dashboard.html",scores=scores,quiz_marks=quiz_marks,timestamp=timestamp,no_questions=no_ques,sub_name=sub_name,chap_name=chap_name,u_name=username,search_val="", search_flag=0) 
    
    except Exception:
        app.logger.warning(f"<!>-- Scores Unable To Load for User ID : {current_user.id} --<!>")
        app.logger.exception('<!> User Score Error')
        return render_template("server_error.html"),500 
    
@app.route("/user/search/scores", methods=["GET","POST"])
@login_required
@roles_required("user")
def user_search_scores():
    try:
        search_str = request.args.get("query_str", "").strip()  
        if(search_str == ""):
            return redirect("/user/scores")
        else:
            scores = []
            quiz_marks = {} # key: score_id, value: quiz_marks
            sub_name = {} # key: score_id, value: subject_name
            chap_name = {} # key: score_id, value: chapter_name
            no_ques = {} # key: score_id, value: count of associated questions
            timestamp = {} # key: score_id, value: [<attempt_date>,<attempt_time>]
            username = "Guest"
            if current_user.is_authenticated:
                u_id = current_user.id 
                username = User_Data.query.filter_by(user_id=u_id).first().full_name
            
            # Filter scores
            if search_str.isdigit(): # filter by quiz id
                scores = Scores.query.filter_by(quiz_id=int(search_str),user_id=current_user.id).all()

            elif(Subjects.query.filter(Subjects.name.like(f"%{search_str}%")).first()): # filter by subject
                temp_sub = Subjects.query.filter(Subjects.name.like(f"%{search_str}%")).all()
                quiz = []
                for sub in temp_sub:
                    quiz += Quiz.query.filter_by(subject_id=sub.id).all()
                for q in quiz:
                    scores += Scores.query.filter_by(quiz_id=q.id,user_id=current_user.id).all()
                
            elif(Chapters.query.filter(Chapters.name.like(f"%{search_str}%")).first()): # filter by chapter
                temp_chap = Chapters.query.filter(Chapters.name.like(f"%{search_str}%")).all()
                quiz = []
                for chap in temp_chap:
                    quiz += Quiz.query.filter_by(chapter_id=chap.id).all()
                for q in quiz:
                    scores += Scores.query.filter_by(quiz_id=q.id,user_id=current_user.id).all()
            
            else: # filter by attempt date 
                try:
                    search_date = dt.strptime(search_str, "%d-%m-%Y").date() # if user query date format is wrong then no result is found
                    scores = Scores.query.filter_by(user_id=current_user.id,attempt_date=search_date).all()
                    
                except:
                    return render_template("user_score_dashboard.html",scores=scores,quiz_marks=quiz_marks,timestamp=timestamp,no_questions=no_ques,sub_name=sub_name,chap_name=chap_name,u_name=username,search_val=search_str, search_flag=1)
                
            scores.reverse()
            for s in scores:
                q = Quiz.query.filter_by(id=s.quiz_id).first()
                timestamp[s.id] = [s.attempt_date.strftime("%d-%m-%Y"), s.attempt_time.strftime("%H:%M:%S") ]
                quiz_marks[s.id] = q.total_marks
                no_ques[s.id] = Questions.query.filter_by(quiz_id=q.id).count()
                if s.id not in sub_name:
                    temp = Chapters.query.filter_by(id=q.chapter_id).first()
                    sub_name[s.id] = Subjects.query.filter_by(id=temp.subject_id).first().name
                    chap_name[s.id] = temp.name
                if s.id not in chap_name:
                    chap_name[s.id] = Chapters.query.filter_by(id=q.chapter_id).first().name

            return render_template("user_score_dashboard.html",scores=scores,quiz_marks=quiz_marks,timestamp=timestamp,no_questions=no_ques,sub_name=sub_name,chap_name=chap_name,u_name=username,search_val=search_str, search_flag=1) 
    
    except Exception:
        app.logger.exception('<!> User Score Search Error')
        return render_template("server_error.html"),500 
    
@app.route("/user/summary", methods=["GET","POST"])
@login_required
@roles_required("user")
def user_summary():
    try:
        username = User_Data.query.filter_by(user_id=current_user.id).first().full_name
        
        scores = Scores.query.filter_by(user_id=current_user.id).all()
        score_count = len(scores)

        # Chart 1: Subject wise performance data
        sub_name = []
        sub_average_score = [] # in percent
        # Chart 2: Quiz Attempts data
        quiz_id = []
        quiz_attempt_count = []
        # Chart 3 : Quiz performance
        scores.reverse()
        recent_quiz_id = []
        recent_quiz_score = [] # in percent

        if (score_count > 0):
            # data extraction for Chart: 3
            for sc in scores:
                temp_quiz = Quiz.query.filter_by(id=sc.quiz_id).first()
                recent_quiz_id += [f'Quiz-{sc.quiz_id}({sc.attempt_date.strftime("%d-%m-%Y")})']
                temp = floor((sc.total_scored / temp_quiz.total_marks) * 100)
                recent_quiz_score += [temp]

            # data extraction for Chart: 1 and 2
            temp_sub = Subjects.query.all() 
            for t in temp_sub:
                attempt_scores = []
                no_quiz = 0
                sub_name += [t.name]
                temp_quiz = Quiz.query.filter_by(subject_id=t.id).all()
                if len(temp_quiz) > 0:
                    for q in temp_quiz:
                        quiz_attempt = Scores.query.filter_by(quiz_id=q.id,user_id=current_user.id).order_by(Scores.total_scored.desc()).all()
                        quiz_id += [f'Quiz-{q.id}']
                        quiz_attempt_count += [len(quiz_attempt)]
                        percent_scored = 0
                        if len(quiz_attempt) > 0:
                            percent_scored = floor((quiz_attempt[0].total_scored / q.total_marks) * 100) # calculating based on the best score obtained from the no. of attempts

                        attempt_scores += [percent_scored]
                        no_quiz += 1

                    sub_average_score += [ceil(sum(attempt_scores) / no_quiz)]


        return render_template("user_summary.html",sub_name=sub_name,sub_average_score=sub_average_score,quiz_id=quiz_id,quiz_attempt_count=quiz_attempt_count,recent_quiz_id=recent_quiz_id,recent_quiz_score=recent_quiz_score,u_name=username,user_score_len=score_count,search_val="", search_flag=0) 

    except Exception:
        app.logger.warning("<!>-- Charts Unable To Load --<!>")
        app.logger.exception('<!> User Summary Error')
        return render_template("server_error.html"),500 
    
@app.route("/user/search/summary", methods=["GET"])
@login_required
@roles_required("user")
def user_search_summary():
    try:
        search_str = request.args.get("query_str", "").strip()  
        if(search_str == ""):
            return redirect("/user/summary")
        else:
            username = User_Data.query.filter_by(user_id=current_user.id).first().full_name
            # Chart 1: Subject wise performance data
            sub_name = []
            sub_average_score = [] # in percent
            # Chart 2: Quiz Attempts data
            quiz_id = []
            quiz_attempt_count = []
            # Chart 3 : Quiz performance
            recent_quiz_id = []
            recent_quiz_score = [] # in percent
            score_count = 0
            try:
                temp_attempt_date = dt.strptime(search_str, "%d-%m-%Y").date() # If date format is not correct
                scores = Scores.query.filter_by(user_id=current_user.id,attempt_date=temp_attempt_date).all()
                scores.reverse()
                score_count = len(scores)
            except:
                return render_template("user_summary.html",sub_name=sub_name,sub_average_score=sub_average_score,quiz_id=quiz_id,quiz_attempt_count=quiz_attempt_count,recent_quiz_id=recent_quiz_id,recent_quiz_score=recent_quiz_score,u_name=username,user_score_len=score_count,search_val=search_str, search_flag=1)
            
            if (score_count > 0):
                # data extraction for Chart: 3
                for sc in scores:
                    temp_quiz = Quiz.query.filter_by(id=sc.quiz_id).first()
                    recent_quiz_id += [f'Quiz-{sc.quiz_id}({sc.attempt_date.strftime("%d-%m-%Y")})']
                    temp = floor((sc.total_scored / temp_quiz.total_marks) * 100)
                    recent_quiz_score += [temp]

                # data extraction for Chart: 1 and 2
                temp_sub = Subjects.query.all() 
                for t in temp_sub:
                    attempt_scores = []
                    no_quiz = 0
                    sub_name += [t.name]
                    temp_quiz = Quiz.query.filter_by(subject_id=t.id).all()
                    if len(temp_quiz) > 0:
                        for q in temp_quiz:
                            quiz_attempt = Scores.query.filter_by(quiz_id=q.id,user_id=current_user.id,attempt_date=temp_attempt_date).order_by(Scores.total_scored.desc()).all()
                            quiz_id += [f'Quiz-{q.id}']
                            quiz_attempt_count += [len(quiz_attempt)]
                            percent_scored = 0
                            if len(quiz_attempt) > 0:
                                percent_scored = floor((quiz_attempt[0].total_scored / q.total_marks) * 100) # calculating based on the best score obtained from the no. of attempts

                            attempt_scores += [percent_scored]
                            no_quiz += 1

                        sub_average_score += [ceil(sum(attempt_scores) / no_quiz)]


            return render_template("user_summary.html",sub_name=sub_name,sub_average_score=sub_average_score,quiz_id=quiz_id,quiz_attempt_count=quiz_attempt_count,recent_quiz_id=recent_quiz_id,recent_quiz_score=recent_quiz_score,u_name=username,user_score_len=score_count,search_val=search_str, search_flag=1) 

    except Exception:
        app.logger.warning("<!>-- Charts Unable To Load --<!>")
        app.logger.exception('<!> User Summary Search Error')
        return render_template("server_error.html"),500 