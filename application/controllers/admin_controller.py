from flask import request, redirect
from flask import render_template
from flask import current_app as app
from flask_security.decorators import login_required, roles_required
from application.models.quiz_model import *
from ..db_base import db
from datetime import datetime
from math import floor, ceil

@app.route("/admin", methods=["GET", "POST"])
@login_required
@roles_required("admin")
def admin():
    try:
        sub = Subjects.query.all()
        sub.reverse()
        chap = {}
        for s in sub:
            chap[s.id] = Chapters.query.filter_by(subject_id=s.id).all()
        return render_template("admin_dashboard.html",subjects=sub,chapters=chap, u_name="Quiz Master", search_val="", search_flag=0, message="") 
    except Exception:
        app.logger.exception('<!> Admin Dashboard Error')
        return render_template("server_error.html"), 500

#Subjects CRUD
@app.route("/admin/add/subject", methods=["POST"])
@login_required
@roles_required("admin")
def create_subject():
    if request.method == "POST":
        sub_name = request.form["subject_name"].strip()
        sub_des = request.form["subject_description"].strip()

        # Check the input fiels are empty or not
        if (sub_name == "") or (sub_des == ""):
            return render_template("alert.html",message="Subject input fields cannot be empty or only spaces.", redirect_after="/admin")

        subject_exist = Subjects.query.filter_by(name=sub_name).first()
        if (subject_exist):
            m = f"Subject with the name '{sub_name}' already exist"
            return render_template("alert.html",message=m, redirect_after="/admin")
        else:
            try:
                if Subjects.query.count() == 0:
                    new_subject = Subjects(
                    id = 4000,
                    name=sub_name,
                    description=sub_des)
                    
                else:
                    new_subject = Subjects(
                    name=sub_name,
                    description=sub_des)
                
                db.session.add(new_subject)
                db.session.flush()

            except Exception:
                db.session.rollback()
                app.logger.exception("<!> Rolling back new subject add commits due to some issue.")
                return render_template("alert.html",message="<!> Subject addition unsuccessful.", redirect_after="/admin")
                
            else:
                db.session.commit()

        return redirect("/admin")
    else: 
        app.logger.warning("<--- Bad Request to '/admin/add/subject' --->")
        return render_template("server_error.html"),500

@app.route("/admin/delete/subject/<int:sub_id>", methods=["POST"])
@login_required
@roles_required("admin")
def delete_subject(sub_id):
    if request.method == "POST":
        try:
            subject = Subjects.query.filter_by(id=sub_id).first()
            db.session.delete(subject)
            db.session.flush()

        except Exception:
            db.session.rollback()
            app.logger.exception(f"<!> Rolling back delete commits for, Subject ID: {sub_id}, due to some issue. ")
            return render_template("alert.html",message="<!> Subject deletion unsuccessful.", redirect_after="/admin")
        else:
            db.session.commit()

        return redirect("/admin")
    
    else: 
        app.logger.warning("<--- Bad Request to '/admin/delete/subject/<int:sub_id>' --->")
        return render_template("server_error.html"),500

@app.route("/admin/edit/subject/<int:sub_id>", methods=["POST"])
@login_required
@roles_required("admin")
def edit_subject(sub_id):
    if request.method == "POST":
        try:
            subject = Subjects.query.filter_by(id=sub_id).first()
            sub_name = request.form["subject_name"].strip()
            sub_des = request.form["subject_description"].strip()

            # Check the input fiels are empty or not
            if (sub_name == "") or (sub_des == ""):
                return render_template("alert.html",message="Subject input fields cannot be empty or only spaces.", redirect_after="/admin")
            
            subject.name = sub_name
            subject.description = sub_des
            db.session.flush()

        except Exception:
            db.session.rollback()
            app.logger.exception(f"<!> Rolling back edit commits for, Subject ID: {sub_id}, due to some issue. ")
            m = f"'{sub_name}' already exist. Please choose another name."
            return render_template("alert.html",message=m, redirect_after="/admin")
        else:
            db.session.commit()

        return redirect("/admin")
    
    else: 
        app.logger.warning("<--- Bad Request to '/admin/edit/subject/<int:sub_id>' --->")
        return render_template("server_error.html"),500

#Chapters CRUD
@app.route("/admin/add/<int:sub_id>/chapter", methods=["POST"])
@login_required
@roles_required("admin")
def add_chapter(sub_id):
    if request.method == "POST":
        chap_name = request.form["chapter_name"].strip()
        chap_des = request.form["chapter_description"].strip()

        # Check the input fiels are empty or not
        if (chap_name == "") or (chap_des == ""):
            return render_template("alert.html",message="Chapter input fields cannot be empty or only spaces.", redirect_after="/admin")

        chapter_exist = Chapters.query.filter((Chapters.name == chap_name) & (Chapters.subject_id == sub_id)).first()
        if (chapter_exist):
            m = f"Chapter with the name '{chap_name}' already exist in the respective subject."
            return render_template("alert.html",message=m, redirect_after="/admin")
            
        else:
            try:
                if Chapters.query.count() == 0:
                    new_chapter = Chapters(
                    id = 5000,
                    subject_id=sub_id,
                    name=chap_name,
                    no_questions=0,
                    description=chap_des)
                    
                else:
                    new_chapter = Chapters(
                    subject_id=sub_id,
                    name=chap_name,
                    no_questions=0,
                    description=chap_des)
                
                db.session.add(new_chapter)
                db.session.flush()

            except Exception:
                db.session.rollback()
                app.logger.exception(f"<!> Rolling back add commits for new chapter under, Subject ID: {sub_id}, due to some issue.")
                return render_template("alert.html",message="<!> Chapter addition unsuccessful.", redirect_after="/admin")
            else:
                db.session.commit()

        return redirect("/admin")
    
    else: 
        app.logger.warning("<--- Bad Request to '/admin/add/<int:sub_id>/chapter' --->")
        return render_template("server_error.html"),500

@app.route("/admin/delete/chapter/<int:chap_id>", methods=["POST"])
@login_required
@roles_required("admin")
def delete_chapter(chap_id):
    if request.method == "POST":
        try:
            chapter = Chapters.query.filter_by(id=chap_id).first()
            db.session.delete(chapter)
            db.session.flush()

        except Exception:
            db.session.rollback()
            app.logger.exception(f"<!> Rolling back delete commits for, Chapter ID: {chap_id}, due to some issue.")
            return render_template("alert.html",message="<!> Chapter deletion unsuccessful.", redirect_after="/admin")
        else:
            db.session.commit()

        return redirect("/admin")
    
    else: 
        app.logger.warning("<--- Bad Request to '/admin/delete/chapter/<int:chap_id>' --->")
        return render_template("server_error.html"),500

@app.route("/admin/edit/chapter/<int:sub_id>/<int:chap_id>", methods=["POST"])
@login_required
@roles_required("admin")
def edit_chapter(sub_id,chap_id):
    if request.method == "POST":
        chap_name = request.form["chapter_name"].strip()
        chap_des = request.form["chapter_description"].strip()
        
        # Check the input fiels are empty or not
        if (chap_name == "") or (chap_des == ""):
            return render_template("alert.html",message="Chapter input fields cannot be empty or only spaces.", redirect_after="/admin")
        
        chapter = Chapters.query.filter_by(id=chap_id).first()
        same_chap_exist = False
        if (chap_name != chapter.name):
            same_chap_exist = Chapters.query.filter((Chapters.name == chap_name) & (Chapters.subject_id == sub_id)).first()
        
        if (same_chap_exist):
            m = f"'{chap_name}' already exist in the respective subject. Please choose another name"
            return render_template("alert.html",message=m, redirect_after="/admin")
        else:
            try:
                chapter.name = chap_name
                chapter.description = chap_des
                db.session.flush()

            except Exception:
                db.session.rollback()
                app.logger.exception(f"<!> Rolling back edit commits for, Chapter ID: {chap_id}, due to some issue.")
                return render_template("alert.html",message="<!> Chapter edit unsuccessful.", redirect_after="/admin")
            else:
                db.session.commit()
        
            return redirect("/admin")
    
    else: 
        app.logger.warning("<--- Bad Request to '/admin/edit/chapter/<int:sub_id>/<int:chap_id>' --->")
        return render_template("server_error.html"),500

@app.route("/admin/search/home", methods=["GET"])
@login_required
@roles_required("admin")
def search_admin_home():
    try:
        search_str = request.args.get("query_str", "").strip()  
        if(search_str == ""):
            return redirect("/admin")
        else:
            sub = Subjects.query.filter(Subjects.name.like(f"%{search_str}%")).all() 
            chap = {}
            if len(sub) == 0:
                sub = []
                temp_chap = Chapters.query.filter(Chapters.name.like(f"%{search_str}%")).all()
                for c in temp_chap:            
                    if c.subject_id not in chap:
                        sub.append(Subjects.query.filter_by(id=c.subject_id).first())
                        chap[c.subject_id] = [c]
                    else:
                        chap[c.subject_id] += [c]
            else:       
                for s in sub:
                    chap[s.id] = Chapters.query.filter_by(subject_id=s.id).all()
            return render_template("admin_dashboard.html",subjects=sub,chapters=chap, u_name="Quiz Master", search_val=search_str, search_flag=1) 
    except Exception:
        app.logger.exception('<!> Admin Home Search Error')
        return render_template("server_error.html"), 500
    

#Quiz CRUD
@app.route("/admin/quiz", methods=["GET","POST"])
@login_required
@roles_required("admin")
def quiz_dashboard():
    try:
        sub = Subjects.query.all()
        sub.reverse()
        quiz = Quiz.query.all()
        quiz.reverse()
        chap = {}
        ques = {}
        options = {}
        q_chap_name = {}
        q_sub_name = {}
        quiz_name = {}
        quiz_duration = {}

        for s in sub:
            chap[s.id] = Chapters.query.filter_by(subject_id=s.id).all()

        for q in quiz:
            ques[q.id] = Questions.query.filter_by(quiz_id=q.id).all()
            quiz_duration[q.id] = q.time_duration.strftime("%H:%M")

            for qu in ques[q.id]:
                options[qu.id] = Options.query.filter_by(question_id=qu.id).all()

            q_sub_name[q.id] = Subjects.query.filter_by(id=q.subject_id).first().name
            q_chap_name[q.id] = Chapters.query.filter_by(id=q.chapter_id).first().name
            # quiz_name[q.id] = "Quiz" + "-" + q_chap_name[q.id] + "(" + q.date_of_quiz.strftime("%d/%m/%Y") + ")"
            quiz_name[q.id] = "Quiz" + "-" + q_chap_name[q.id] + "-" + str(q.id) 

        return render_template("admin_quiz_dashboard.html",subjects=sub,chapters=chap,q_sub_name=q_sub_name,q_chap_name=q_chap_name,quizzes=quiz,q_name=quiz_name,duration=quiz_duration,questions=ques,options=options,u_name="Quiz Master",search_val="", search_flag=0)
    
    except Exception:
        app.logger.exception('<!> Quiz Dashboard Error')
        return render_template("server_error.html"),500 
    
@app.route("/admin/search/quiz", methods=["GET"])
@login_required
@roles_required("admin")
def search_admin_quiz():
    try:
        search_str = request.args.get("query_str", "").strip()  
        if(search_str == ""):
            return redirect("/admin/quiz")
        else:
            quiz = []
            sub = []
            chap = {}
            ques = {}
            options = {}
            q_chap_name = {}
            q_sub_name = {}
            quiz_name = {}
            quiz_duration = {}
            filter_by_ques_title = False
            
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
            
            elif(Questions.query.filter(Questions.question_title.like(f"%{search_str}%")).first()): # filter by question title
                filter_by_ques_title = True
                temp_ques = Questions.query.filter(Questions.question_title.like(f"%{search_str}%")).all()
                for qu in temp_ques:    
                    if qu.quiz_id in ques:
                        ques[qu.quiz_id] += [qu]
                    else:
                        ques[qu.quiz_id] = [qu]
                        quiz += Quiz.query.filter_by(id=qu.quiz_id).all()
                        
            else: # filter by date of quiz
                try:
                    search_date = datetime.strptime(search_str, "%d-%m-%Y").date() 
                    quiz = Quiz.query.filter_by(date_of_quiz=search_date).all()
                
                except: # if the date format has any error then no result
                    return render_template("admin_quiz_dashboard.html",subjects=sub,chapters=chap,q_sub_name=q_sub_name,q_chap_name=q_chap_name,quizzes=quiz,q_name=quiz_name,duration=quiz_duration,questions=ques,options=options,u_name="Quiz Master", search_val=search_str, search_flag=1)

            for q in quiz:
                if not filter_by_ques_title:
                    ques[q.id] = Questions.query.filter_by(quiz_id=q.id).all()

                quiz_duration[q.id] = q.time_duration.strftime("%H:%M")

                for qu in ques[q.id]:
                    options[qu.id] = Options.query.filter_by(question_id=qu.id).all()

                q_sub_name[q.id] = Subjects.query.filter_by(id=q.subject_id).first().name
                q_chap_name[q.id] = Chapters.query.filter_by(id=q.chapter_id).first().name
                quiz_name[q.id] = "Quiz" + "-" + q_chap_name[q.id] + "-" + str(q.id) 

        return render_template("admin_quiz_dashboard.html",subjects=sub,chapters=chap,q_sub_name=q_sub_name,q_chap_name=q_chap_name,quizzes=quiz,q_name=quiz_name,duration=quiz_duration,questions=ques,options=options,u_name="Quiz Master", search_val=search_str, search_flag=1) 
    
    except Exception:
        app.logger.exception('<!> Admin Search Quiz Error')
        return render_template("server_error.html"), 500

@app.route("/admin/add/quiz", methods=["POST"])
@login_required
@roles_required("admin")
def create_quiz():
    if request.method == "POST":
        sub_id = int(request.form["subject_id"])
        chap_id = int(request.form["chapter_id"])
        q_date = datetime.strptime(request.form["quiz_date"], "%Y-%m-%d").date()

        # Check for quiz date
        current_date = datetime.now().date()
        if q_date < current_date:
            return render_template("alert.html",message="Quiz date must be on the current date or passed that.", redirect_after="/admin/quiz")

        same_quiz_exist = Quiz.query.filter((Quiz.date_of_quiz == q_date) & (Quiz.chapter_id == chap_id)).first()

        if (same_quiz_exist):
            m = "A quiz on the same chapter and date already exist. Please choose another date."
            return render_template("alert.html",message=m, redirect_after="/admin/quiz")
        
        else:
            try:
                q_dura  = datetime.strptime(request.form["quiz_duration"], "%H:%M").time()
                if Quiz.query.count() == 0:
                    new_quiz = Quiz(
                    id = 6000,
                    subject_id = sub_id,
                    chapter_id = chap_id,
                    date_of_quiz = q_date,
                    time_duration = q_dura,
                    total_marks = 0,
                    remarks = 0)
                    
                else:
                    new_quiz = Quiz(
                    subject_id = sub_id,
                    chapter_id = chap_id,
                    date_of_quiz = q_date,
                    time_duration = q_dura,
                    total_marks = 0,
                    remarks = 0)
                
                db.session.add(new_quiz)
                db.session.flush()
            
            except Exception:
                db.session.rollback()
                app.logger.exception(f"<!> Rolling back quiz add commits for, Chapter ID: {chap_id}, due to some issue.")
                return render_template("alert.html",message="<!> Quiz addition unsuccessful.", redirect_after="/admin/quiz")
            else:
                db.session.commit()
            
            return redirect("/admin/quiz")

    else: 
        app.logger.warning("<--- Bad Request to '/admin/add/quiz' --->")
        return render_template("server_error.html"),500
   
@app.route("/admin/delete/quiz/<int:quiz_id>", methods=["POST"])
@login_required
@roles_required("admin")
def delete_quiz(quiz_id):
    if request.method == "POST":
        try:
            quiz = Quiz.query.filter_by(id=quiz_id).first()
            no_ques = Questions.query.filter_by(quiz_id=quiz_id).count()
            chap = Chapters.query.filter_by(id=quiz.chapter_id).first()
            chap.no_questions -= no_ques
            db.session.delete(quiz)
            db.session.flush()

        except Exception:
            db.session.rollback()
            app.logger.exception(f"<!> Rolling back delete commits for, Quiz ID: {quiz_id}, due to some issue.")
            return render_template("alert.html",message="<!> Quiz addition unsuccessful.", redirect_after="/admin/quiz")
        else:
            db.session.commit()

        return redirect("/admin/quiz")
    
    else: 
        app.logger.warning("<--- Bad Request to '/admin/delete/quiz/<int:quiz_id>' --->")
        return render_template("server_error.html"),500

@app.route("/admin/edit/quiz/<int:quiz_id>", methods=["POST"])
@login_required
@roles_required("admin")
def edit_quiz(quiz_id):
    if request.method == "POST":
            quiz = Quiz.query.filter_by(id=quiz_id).first()
            q_date = datetime.strptime(request.form["quiz_date"], "%Y-%m-%d").date()
            same_quiz_exist = False

            # Check for quiz date
            current_date = datetime.now().date()
            if q_date < current_date:
                return render_template("alert.html",message="Quiz date must be on the current date or passed that.", redirect_after="/admin/quiz")
            
            if (quiz.date_of_quiz != q_date):
                same_quiz_exist = Quiz.query.filter((Quiz.date_of_quiz == q_date) & (Quiz.chapter_id == quiz.chapter_id)).first()

            if (same_quiz_exist):
                m = 'A quiz on the same chapter and date already exist. Please choose another date.'
                return render_template("alert.html",message=m, redirect_after="/admin/quiz")
            
            else:
                try:     
                    q_duration  = datetime.strptime(request.form["quiz_duration"], "%H:%M").time()
                    quiz.date_of_quiz = q_date
                    quiz.time_duration = q_duration
                    db.session.flush()

                except Exception:
                    db.session.rollback()
                    app.logger.exception(f"<!> Rolling back edit commits for, Quiz ID: {quiz_id}, due to some issue.")
                    return render_template("alert.html",message="<!> Quiz edit unsuccessful.", redirect_after="/admin/quiz")
                else:
                    db.session.commit()

                return redirect("/admin/quiz")
    
    else: 
        app.logger.warning("<--- Bad Request to '/admin/edit/quiz/<int:quiz_id>' --->")
        return render_template("server_error.html"),500

def insert_option(question_id,op_statement,op_no):
    try:
        if Options.query.count() == 0:
            new_option = Options(
            id = 8000,
            question_id = question_id,
            option_no = op_no,
            option_statement = op_statement)
        else:
            new_option = Options(
            question_id = question_id,
            option_no = op_no,
            option_statement = op_statement)

        db.session.add(new_option)

    except:
        db.session.rollback()
        raise Exception("<!> Option Insertion Failed")
    else:
        db.session.commit()
                    
@app.route("/admin/add/<int:quiz_id>/question", methods=["POST"])
@login_required
@roles_required("admin")
def add_question(quiz_id):
    if request.method == "POST":
        # Check if a quiz attempt already exist, block the operation
        if(Scores.query.filter_by(quiz_id=quiz_id).first()):
            return render_template("alert.html",message=f"<!> New question cannot be added to the Quiz - {quiz_id}. Some user has already attempted the quiz. This operation could lead to score anomalies.", redirect_after="/admin/quiz")

        q_title = request.form["question_title"].strip()
        q_statement = request.form["question_statement"].strip()
        op1 = request.form["option1"].strip()
        op2 = request.form["option2"].strip()
        op3 = request.form["option3"].strip()
        op4 = request.form["option4"].strip()
        
        if (q_title == "") or (q_statement == "") or (op1 == "") or (op2 == "") or (op3 == "") or (op4 == ""):
            return render_template("alert.html",message="Question input fields can not be empty or only spaces.", redirect_after="/admin/quiz")
        try:
            q_marks = int(request.form["question_marks"])
            if q_marks < 1:
                raise Exception
        except:
            return render_template("alert.html",message="Question marks must be greater than 0.", redirect_after="/admin/quiz")
        try:
            correct_op = int(request.form["correct_option"])
            if correct_op not in [1,2,3,4]:
                raise Exception
        except:
            return render_template("alert.html",message="Question's correct option must be choosen from the list.", redirect_after="/admin/quiz")

        question_exist = Questions.query.filter((Questions.question_title == q_title) & (Questions.quiz_id == quiz_id)).first()
        
        if (question_exist):
            m = f"Question with the title '{q_title}' already exist inside the respective quiz"
            return render_template("alert.html",message=m, redirect_after="/admin/quiz")
            
        else:
            try:
                if Questions.query.count() == 0:
                    new_question = Questions(
                    id = 7000,
                    quiz_id = quiz_id,
                    marks = q_marks,
                    question_title = q_title,
                    question_statement = q_statement,
                    question_type = "M.C.Q",
                    correct_option = correct_op)
                    
                else:
                    new_question = Questions(
                    quiz_id = quiz_id,
                    marks = q_marks,
                    question_title = q_title,
                    question_statement = q_statement,
                    question_type = "M.C.Q",
                    correct_option = correct_op)
                
                db.session.add(new_question)
                
                Qz = Quiz.query.filter_by(id=quiz_id).first()
                Qz.total_marks += q_marks
                chap = Chapters.query.filter_by(id=Qz.chapter_id).first()
                chap.no_questions += 1
                db.session.flush()

                insert_option(new_question.id,op1,1)
                insert_option(new_question.id,op2,2)
                insert_option(new_question.id,op3,3)
                insert_option(new_question.id,op4,4)

            except Exception:
                db.session.rollback()
                app.logger.exception(f"<!> Rolling back question add commits for, Quiz ID: {quiz_id}, due to some issue.")
                return render_template("alert.html",message="<!> Question addition unsuccessful.", redirect_after="/admin/quiz")
            else:
                db.session.commit()
            
            return redirect("/admin/quiz")

    else: 
        app.logger.warning("<--- Bad Request to '/admin/add/<int:quiz_id>/question' --->")
        return render_template("server_error.html"),500

@app.route("/admin/delete/question/<int:quiz_id>/<int:question_id>", methods=["POST"])
@login_required
@roles_required("admin")
def delete_question(quiz_id,question_id):
    if request.method == "POST":
        # Check if a quiz attempt already exist, block the operation
        if(Scores.query.filter_by(quiz_id=quiz_id).first()):
            return render_template("alert.html",message=f"<!> Question cannot be deleted from the Quiz - {quiz_id}. Some user has already attempted the quiz. This operation could lead to score anomalies.", redirect_after="/admin/quiz")
        
        try:
            question = Questions.query.filter_by(id=question_id).first()

            Qz = Quiz.query.filter_by(id=quiz_id).first()
            Qz.total_marks -= int(question.marks)       
            chap = Chapters.query.filter_by(id=Qz.chapter_id).first()
            chap.no_questions -= 1
            db.session.flush()
            
            db.session.delete(question)
            db.session.flush()

        except Exception:
            db.session.rollback()
            app.logger.exception(f"<!> Rolling back delete commits for, Question ID: {question_id}, due to some issue.")
            return render_template("alert.html",message="<!> Question deletion unsuccessful.", redirect_after="/admin/quiz")
        else:
            db.session.commit()

        return redirect("/admin/quiz")
    
    else: 
        app.logger.warning("<--- Bad Request to '/admin/delete/question/<int:quiz_id>/<int:question_id>' --->")
        return render_template("server_error.html"),500
    
@app.route("/admin/edit/question/<int:quiz_id>/<int:question_id>", methods=["POST"])
@login_required
@roles_required("admin")
def edit_question(quiz_id,question_id):
    if request.method == "POST":
        # Check if a quiz attempt already exist, block the operation
        if(Scores.query.filter_by(quiz_id=quiz_id).first()):
            return render_template("alert.html",message=f"<!> Question cannot be edited for the Quiz - {quiz_id}. Some user has already attempted the quiz. This operation could lead to score anomalies.", redirect_after="/admin/quiz")
        
        q_title = request.form["question_title"].strip()
        q_statement = request.form["ques_statement"].strip()
        op = [request.form["option1"].strip(),request.form["option2"].strip(),request.form["option3"].strip(),request.form["option4"].strip()]

        if (q_title == "") or (q_statement == "") or (op[0] == "") or (op[1] == "") or (op[2] == "") or (op[3] == ""):
            return render_template("alert.html",message="Question input fields can not be empty or only spaces.", redirect_after="/admin/quiz")
        try:
            q_marks = int(request.form["question_marks"])
            if q_marks < 1:
                raise Exception
        except:
            return render_template("alert.html",message="Question marks must be greater than 0.", redirect_after="/admin/quiz")
        try:
            correct_op = int(request.form["correct_option"])
            if correct_op not in [1,2,3,4]:
                raise Exception
        except:
            return render_template("alert.html",message="Question's correct option must be choosen from the list.", redirect_after="/admin/quiz")

        ques = Questions.query.filter_by(id=question_id).first()
        same_ques_exist = False

        if (q_title != ques.question_title):
            same_ques_exist = Questions.query.filter((Questions.question_title == q_title) & (Questions.quiz_id == quiz_id)).first()
        
        if (same_ques_exist):
            m = f"'{q_title}' already exist. Please choose another name."
            return render_template("alert.html",message=m, redirect_after="/admin/quiz")
        
        else:
            try:         
                ques.question_title = q_title
                prev_marks = ques.marks
                ques.marks = q_marks
                ques.question_statement = q_statement
                ques.correct_option = correct_op
                db.session.flush()
                
                if(prev_marks != q_marks):
                    Qz = Quiz.query.filter_by(id=quiz_id).first()
                    # if previous question marks is greater than the new marks then decrease the value of total marks and vice versa.
                    if (prev_marks > q_marks):
                        Qz.total_marks -= (prev_marks - q_marks)
                    elif (prev_marks < q_marks):
                        Qz.total_marks += (q_marks - prev_marks)
                    db.session.flush()

                # To update the options
                ques_options = Options.query.filter_by(question_id=question_id).all()
                for i in range(4):
                    ques_options[i].option_statement = op[i]
                    db.session.flush()

            except Exception:
                db.session.rollback()
                app.logger.exception(f"<!> Rolling back edit commits for, Question ID: {question_id}, due to some issue.")
                return render_template("alert.html",message="<!> Question edit unsuccessful.", redirect_after="/admin/quiz")
            else:
                db.session.commit()

            return redirect("/admin/quiz")
    
    else: 
        app.logger.warning("<--- Bad Request to '/admin/edit/question/<int:quiz_id>/<int:question_id>' --->")
        return render_template("server_error.html"),500
    
@app.route("/admin/summary", methods=["GET","POST"])
@login_required
@roles_required("admin")
def admin_summary():
    try:
        username = "Quiz Master"
        
        scores = Scores.query.all()
        total_score_count = len(scores)

        sub_name = []
        # Chart 1: Subject wise quiz attempt data
        sub_user_attempts = []
        # Chart 2: Number of quizzes for a subject data
        quiz_count = []
        # Chart 3 : Subject wise top score
        top_score = [] # in percent
       
        if (total_score_count > 0):
            # data extraction for Chart: 1 and 2 and 3
            sub = Subjects.query.all()
            for t in sub:
                attempt_scores = []
                no_quiz = 0
                attempt_count = 0
                sub_name += [t.name]
                temp_quiz = Quiz.query.filter_by(subject_id=t.id).all()
                quiz_count += [len(temp_quiz)]
                if len(temp_quiz) > 0:
                    for q in temp_quiz:
                        quiz_attempt = Scores.query.filter_by(quiz_id=q.id).order_by(Scores.total_scored.desc()).all()
                        attempt_count += len(quiz_attempt)
                        percent_scored = 0
                        if len(quiz_attempt) > 0:
                            percent_scored = floor((quiz_attempt[0].total_scored / q.total_marks) * 100) # calculating based on the best score obtained from the no. of attempts

                        attempt_scores += [percent_scored]
                        no_quiz += 1

                    sub_user_attempts += [attempt_count]
                    top_score += [ceil(sum(attempt_scores) / no_quiz)]

        return render_template("admin_summary.html",sub_name=sub_name,sub_user_attempts=sub_user_attempts,quiz_count=quiz_count,top_score=top_score,u_name=username,user_score_len=total_score_count,search_val="",search_flag=0) 

    except Exception:
        app.logger.warning("<!>-- Charts Unable To Load --<!>")
        app.logger.exception('<!> Admin Summary Error')
        return render_template("server_error.html"),500 
    
@app.route("/admin/search/summary", methods=["GET"])
@login_required
@roles_required("admin")
def admin_search_summary():
    try:
        search_str = request.args.get("query_str", "").strip()  
        if(search_str == ""):
            return redirect("/admin/summary")
        else:
            username = "Quiz Master"
            if search_str.isdigit(): # filter by user id
                scores = Scores.query.filter_by(user_id=int(search_str)).all()
                total_score_count = len(scores)
            else:
                total_score_count = 0

            sub_name = []
            # Chart 1: Subject wise quiz attempt data
            sub_user_attempts = []
            # Chart 2: Number of quizzes for a subject data
            quiz_count = []
            # Chart 3 : Subject wise top score
            top_score = [] # in percent
        

            if (total_score_count > 0):
                # data extraction for Chart: 1 and 2 and 3
                sub = Subjects.query.all()
                for t in sub:
                    attempt_scores = []
                    no_quiz = 0
                    attempt_count = 0
                    sub_name += [t.name]
                    temp_quiz = Quiz.query.filter_by(subject_id=t.id).all()
                    quiz_count += [len(temp_quiz)]
                    if len(temp_quiz) > 0:
                        for q in temp_quiz:
                            quiz_attempt = Scores.query.filter_by(quiz_id=q.id,user_id=int(search_str)).order_by(Scores.total_scored.desc()).all()
                            attempt_count += len(quiz_attempt)
                            percent_scored = 0
                            if len(quiz_attempt) > 0:
                                percent_scored = floor((quiz_attempt[0].total_scored / q.total_marks) * 100) # calculating based on the best score obtained from the no. of attempts
                            attempt_scores += [percent_scored]
                            no_quiz += 1

                        sub_user_attempts += [attempt_count]
                        top_score += [ceil(sum(attempt_scores) / no_quiz)]

                top_score.sort(reverse=True)
                
            return render_template("admin_summary.html",sub_name=sub_name,sub_user_attempts=sub_user_attempts,quiz_count=quiz_count,top_score=top_score,u_name=username,user_score_len=total_score_count,search_val=search_str,search_flag=1) 

    except Exception:
        app.logger.warning("<!>-- Charts Unable To Load --<!>")
        app.logger.exception('<!> Admin Summary Search Error')
        return render_template("server_error.html"),500 