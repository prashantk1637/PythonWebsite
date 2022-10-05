from techbasics import app
from techbasics import db
from flask import request, flash, redirect, render_template,session,jsonify
from techbasics.models import Users,Posts,Questions,Courses,PageVisitors,QuestionSimilarity,MCQ
from datetime import datetime
from dateutil.tz import gettz
from sqlalchemy import func
import logging
import re
from numpy import dot
import pandas as pd
import sqlite3
from numpy.linalg import norm
import itertools
import random
import json
#Main and home routes===========================================================================
@app.route("/")
def index():
    db.create_all()
    count=0
    if not session.get("user"):
        remote_addr=str(request.environ.get('HTTP_X_FORWARDED_FOR',request.remote_addr))
        dtobj = datetime.now(tz=gettz('Asia/Calcutta'))
        t=dtobj.strftime("%b %d %Y")
        old_visit=db.session.query(PageVisitors.id).filter((PageVisitors.remote_ip==remote_addr) & (PageVisitors.visit_time==t))
        if old_visit.count()==1:
            #PageVisitors.query.filter((PageVisitors.remote_ip==remote_addr) & (PageVisitors.visit_time==t)).update({"visit_count": (PageVisitors.visit_count +1)})
            #db.session.commit()
            count=PageVisitors.query.count()
        else:
            pagevisit = PageVisitors(remote_addr,1)
            db.session.add(pagevisit)
            db.session.commit()
            count=PageVisitors.query.count()

        courses=db.session.query(Courses.id,Courses.course_fullname,func.count(Questions.course_id)).filter(Courses.id == Questions.course_id).group_by(Questions.course_id).all()
        return render_template('index.html',courses=courses,pagevisit_count=count)
    else:
        return redirect('/home')

@app.route('/home')
def homePage():
    if not session.get("user"):
        return redirect('/login-user')
    else:
        remote_addr=str(request.environ.get('HTTP_X_FORWARDED_FOR',request.remote_addr))
        dtobj = datetime.now(tz=gettz('Asia/Calcutta'))
        t=dtobj.strftime("%b %d %Y")
        old_visit=db.session.query(PageVisitors.id).filter((PageVisitors.remote_ip==remote_addr) & (PageVisitors.visit_time==t))
        count=0
        if old_visit.count()==1:
            #PageVisitors.query.filter((PageVisitors.remote_ip==remote_addr) & (PageVisitors.visit_time==t)).update({"visit_count": (PageVisitors.visit_count +1)})
            #db.session.commit()
            count=PageVisitors.query.count()
        else:
            pagevisit = PageVisitors(remote_addr,1)
            db.session.add(pagevisit)
            db.session.commit()
            count=PageVisitors.query.count()
        courses=db.session.query(Courses.id,Courses.course_fullname,func.count(Questions.course_id)).filter(Courses.id == Questions.course_id).group_by(Questions.course_id).all()
        return render_template('/homePage/index.html',courses=courses,pagevisit_count=count)

#login routes====================================================================================
@app.route('/login-user')
def login_user():
    redirect_uri=request.args.get('redirect_uri','/home')
    error=request.args.get('error','')
    return render_template('/login-user/index.html',redirect_uri=redirect_uri,error=error)

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email=request.form['email']
        password=request.form['password']
        redirect_uri=request.form['redirect_uri']
        result=Users.query.filter((Users.email==email) & (Users.password==password))
        if result.count()==1:
            session['user'] =result[0].email
            session['user_type'] =result[0].type
            session['name']  = result[0].name
            session['is_active']  = result[0].is_active
            return redirect(redirect_uri)
        else:
            return redirect('/login-user?redirect_uri='+redirect_uri+'&error=Invalid User')
    else:
        return 'Invalid request'

#signup routes====================================================================================
@app.route('/signup-user')
def signup_user():
    return render_template('/login-user/signup.html')

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        user = Users(request.form['email'], request.form['password'],request.form['name'])
        db.session.add(user)
        db.session.commit()
        flash('User registered')
        return redirect('/login-user')
    else:
        return "Invalid request"

@app.route('/logout')
def logout():
     session['user'] =None
     session['user_type'] =None
     session['name']=None
     session['is_active']=None
     return redirect('/')

#Discussion area routes=========================================================================

@app.route('/discussion-area')
def discussion_area():
    return render_template('/discussion-area/index.html',posts=Posts.query.all())
@app.route('/add_post',methods=['GET','POST'])
def add_post():
    if request.method == 'POST':
        guest=str(request.environ['HTTP_X_FORWARDED_FOR']).split('.')
        guest_name='Guest'+str(int(guest[0])+22)+str(int(guest[1])*4)+str(int(guest[2])*3)+str(int(guest[3])+23)
        post=Posts(request.form['post'],guest_name)
        db.session.add(post)
        db.session.commit()
        return redirect('/discussion-area')
    else:
        return 'Invalid request'



#Add questions/courses routes=========================================================================
@app.route('/add-question')
def add_question():
    if not session.get("user"):
        redirect_uri='/add-question'
        return redirect('/login-user?redirect_uri='+str(redirect_uri))
    elif session.get("is_active")=="yes":
        return render_template('/add-question/index.html',courses=Courses.query.order_by(Courses.course_fullname).all())
    else:
        return "Sorry your account is not activated yet"


@app.route('/new-question',methods=['GET','POST'])
def question_entry():
    if not session.get("user"):
        return redirect('/login-user')
    elif session.get("is_active")=="yes":
        if request.method == 'POST':
            tags=str(request.form['question']).replace(' ','#')
            question = Questions(request.form['question'],request.form['answer'],request.form['question-category-id'],tags)
            db.session.add(question)
            db.session.commit()
            return render_template('/add-question/index.html',string1="Question is added successfully",courses=Courses.query.all())
        else:
            return 'Invalid request'
    else:
        return "Sorry your account is not activated yet"

@app.route('/add-course')
def add_course():
    if not session.get("user"):
        redirect_uri='/add-course'
        return redirect('/login-user?redirect_uri='+str(redirect_uri))
    elif session.get("is_active")=="yes":
        return render_template('/add-question/newcourse.html')
    else:
        return "Sorry your account is not activated yet"

@app.route('/new-course',methods=['GET','POST'])
def new_course():
    if not session.get("user"):
        return redirect('/login-user')
    elif session.get("is_active")=="yes":
        if request.method == 'POST':
            new_course = Courses(request.form['course_name'])
            db.session.add(new_course)
            db.session.commit()
            return render_template('/add-question/newcourse.html',string1="New Course has been is created")
        else:
            return 'Invalid request'
    else:
        return "Sorry your account is not activated yet"

#Code Section================================================================================
@app.route('/code-section')
def code_section():
    return render_template('/code-section/index.html')

@app.route('/run-code',methods=['GET','POST'])
def run_code():
    if request.method == 'POST':
            import os
            #lang=request.form['language']
            #code=request.form['code']
            content = request.get_json()
            lang=content['language']
            code=content['code']
            rand=random.randint(1,999999)
            output_filename='output'+str(rand)+'.txt'
            error_filename='error'+str(rand)+'.txt'
            path='./compiler/'
            output_filename=path+output_filename
            error_filename=path+error_filename
            lines=""
            if lang=="Python":
                code=re.sub(r'import\s+os','',code)
                code=re.sub(r'import\s+subprocess','',code)
                code=re.sub(r'/data/','mysite/techbasics/static/data/',code)
                python_sourcefile='python'+str(rand)+'.py'
                python_sourcefile='./compiler/'+python_sourcefile
                py_file = open(python_sourcefile, 'w')
                py_file.write(code)
                py_file.close()
                ret_val=os.system('python '+python_sourcefile+' 1> '+output_filename+' 2> '+error_filename)
                if ret_val==0:
                    out_file=open(output_filename, 'r')
                    for line in out_file.readlines():
                        lines=lines+line+'#';
                    out_file.close()
                else:
                    out_file=open(error_filename, 'r')
                    for line in out_file.readlines():
                        lines=lines+line+'#';
                    out_file.close()
                    lines=lines.replace('/home/techbasics/'+python_sourcefile,'solution.py')
                os.system('rm -f '+python_sourcefile)
            if lang=="Java":
                replace_pattern =r'class\s+[A-Z]*[a-z]*\s*{'
                search_pattern=r'class\s+[A-Z]*[a-z]*\s*{\s*public\s+static\s+void main'
                span=re.search(search_pattern,code).span()
                code_segment1=code[0:span[0]]
                code_segment2=code[span[0]:span[1]]
                code_segment2=re.sub(replace_pattern,'class Solution{',code_segment2)
                code_segment3=code[span[1]:-1]
                code=code_segment1+code_segment2+code_segment3+' }' ##one bracket is missing somehow so adding it.. need to debug why..
                java_sourcefile='Java'+str(rand)+'.java'
                java_sourcefile='./compiler/'+java_sourcefile
                java_file = open(java_sourcefile, 'w')
                java_file.write(code)
                java_file.close()
                ret_val=os.system('javac '+java_sourcefile+' 1> '+output_filename+' 2> '+error_filename)
                if ret_val==0:
                    os.system('cd compiler|java Solution 1> '+output_filename+' 2> '+error_filename)
                    out_file=open(output_filename, 'r')
                    for line in out_file.readlines():
                        lines=lines+line+'#';
                    out_file.close()
                else:
                    out_file=open(error_filename, 'r')
                    for line in out_file.readlines():
                        lines=lines+line+'#';
                    out_file.close()
                #os.system('rm -f '+java_sourcefile)

            if lang=="C":
                c_file = open('solution.c', 'w')
                c_file.write(code)
                c_file.close()
                ret_val=os.system('gcc solution.c -o solution' + ' 1> '+output_filename+' 2> '+error_filename)
                if ret_val==0:
                    os.system('./compiler/solution' + ' 1> '+output_filename+' 2> '+error_filename)
                    out_file=open(output_filename, 'r')
                    for line in out_file.readlines():
                        lines=lines+line+'#';
                    out_file.close()
                else:
                    out_file=open(error_filename, 'r')
                    for line in out_file.readlines():
                        lines=lines+line+'#';
                    out_file.close()

            if lang=="cpp":
                cpp_file = open('solution.cpp', 'w')
                cpp_file.write(code)
                cpp_file.close()
                ret_val=os.system('g++ solution.cpp -o solution1' + ' 1> '+output_filename+' 2> '+error_filename)
                if ret_val==0:
                    os.system('./solution1' + ' 1> '+output_filename+' 2> '+error_filename)
                    out_file=open(output_filename, 'r')
                    for line in out_file.readlines():
                       lines=lines+line+'#';
                    out_file.close()
                else:
                    out_file=open(error_filename, 'r')
                    for line in out_file.readlines():
                        lines=lines+line+'#';
                    out_file.close()

            os.system('rm -f '+output_filename)
            os.system('rm -f '+error_filename)

            return lines
    else:
        return 'Invaild request'
#Admin Panel========================================================

@app.route('/admin-panel')
def admin_panel():
    if not session.get("user"):
        redirect_uri='/admin-panel'
        return redirect('/login-user?redirect_uri='+str(redirect_uri))
    else:
        if session.get("user_type")=='admin':
            tables = db.session.execute("select sql from sqlite_master where type='table'")
            table_list=[]
            for table in tables:
                dict1=dict(table.items())
                str1=dict1['sql']
                str1=re.sub(r'(\([0-9]+)\)','',str1)
                str1=re.sub(r'(\([a-z]+)\)','',str1)
                table_list.append(str1.split(','))
            return render_template('/admin-panel/index.html',table_list=table_list)
        else:
            return 'access denied'

@app.route('/run-sql',methods=['GET','POST'])
def run_sql():
    if request.method == 'POST':
        if not session.get("user"):
            return redirect('/login-user')
        else:
            if session.get("user_type")=='admin':
                tables = db.session.execute("select sql from sqlite_master where type='table'")
                table_list=[]
                for table in tables:
                    dict1=dict(table.items())
                    str1=dict1['sql']
                    str1=re.sub(r'(\([0-9]+)\)','',str1)
                    str1=re.sub(r'(\([a-z]+)\)','',str1)
                    table_list.append(str1.split(','))
                sql=request.form['sql']
                first_word=sql.split(" ")[0]
                startwith=re.findall(r'^(delete|select|update|insert|drop|alter|create|rename)',first_word.lower())
                if len(startwith)==0:
                    startwith=['default']
                if str(startwith[0]).upper()=="SELECT":
                    result = db.session.execute(sql)
                    row_list=[]
                    for row in result:
                        row_list.append(dict(row.items()))
                    return render_template('/admin-panel/index.html',sql_data=row_list,table_list=table_list)

                if str(startwith[0]).upper()=="DELETE":
                    db.session.execute(sql)
                    db.session.commit()
                    sql_data="data got deleted"
                    return render_template('/admin-panel/index.html',sql_data=sql_data,table_list=table_list)

                if str(startwith[0]).upper()=="UPDATE":
                    db.session.execute(sql)
                    db.session.commit()
                    sql_data="data got updated"
                    return render_template('/admin-panel/index.html',sql_data=sql_data,table_list=table_list)
                if str(startwith[0]).upper()=="INSERT":
                    db.session.execute(sql)
                    db.session.commit()
                    sql_data="data got inserted"
                    return render_template('/admin-panel/index.html',sql_data=sql_data,table_list=table_list)
                if str(startwith[0]).upper()=="DROP":
                    db.session.execute(sql)
                    db.session.commit()
                    sql_data="table got dropped"
                    return render_template('/admin-panel/index.html',sql_data=sql_data,table_list=table_list)

                if str(startwith[0]).upper()=="ALTER":
                    db.session.execute(sql)
                    db.session.commit()
                    sql_data="table has been altered"
                    return render_template('/admin-panel/index.html',sql_data=sql_data,table_list=table_list)

                if str(startwith[0]).upper()=="CREATE":
                    db.session.execute(sql)
                    db.session.commit()
                    sql_data="table has been created"
                    return render_template('/admin-panel/index.html',sql_data=sql_data,table_list=table_list)

                if str(startwith[0]).upper()=="RENAME":
                    db.session.execute(sql)
                    db.session.commit()
                    sql_data="table has been renamed"
                    return render_template('/admin-panel/index.html',sql_data=sql_data,table_list=table_list)
                else:
                    return "Syntax error"

    else:
        return 'invalid request'

#Tutorial route==========================================================================================================================================================
@app.route('/<int:tutorial_id>')
def display_questions(tutorial_id):
    if tutorial_id==17:  ##restrict access on kiwi tutorial
        if session.get("user") and session.get("user_type")=='admin':
            tutorial_name=Courses.query.filter(Courses.id==tutorial_id)
            if tutorial_name.count()==1:
                kiwi_data=pd.read_csv('/home/techbasics/kiwi_data.csv')
                logging.info(kiwi_data.head())
                return render_template('/display-questions/index.html',questions=db.session.query(Questions.id,Questions.question,Questions.answer,Questions.tags).filter(Questions.course_id==tutorial_id).order_by(Questions.id),tutorial_name=tutorial_name,kiwi_data=kiwi_data)
                #return render_template('/display-questions/index.html',tutorial_name=tutorial_name,kiwi_data=kiwi_data)
            else:
                tutorial_name=[{"course_fullname":"Not Found Any Tutorial"}]
                return render_template('/display-questions/index.html',tutorial_name=tutorial_name)
        else:
            return 'Access denied'

    else:
        tutorial_name=Courses.query.filter(Courses.id==tutorial_id)
        if tutorial_name.count()==1:
            return render_template('/display-questions/index.html',questions=db.session.query(Questions.id,Questions.question,Questions.answer,Questions.tags).filter(Questions.course_id==tutorial_id).order_by(Questions.id),tutorial_name=tutorial_name)
        else:
            tutorial_name=[{"course_fullname":"Not Found Any Tutorial"}]
            return render_template('/display-questions/index.html',tutorial_name=tutorial_name)


#===upate answer of a question



@app.route('/api/update/<int:question_id>',methods=['GET','PUT'])
def update_answer(question_id):
    if request.method == 'PUT':
        if session.get("user_type")=='admin':
            content = request.get_json()
            answer=content['value']
            #logging.info(answer)
            Questions.query.filter(Questions.id==question_id).update({"answer":answer})
            db.session.commit()
            return 'Updated'
        else:
            return 'access denied'
    else:
        return 'Invaild request'


#===================
#contact me=================================================================================================================================================================
@app.route('/email')
def email_me():
    return render_template('/email/index.html')

@app.errorhandler(404)
def invalid_route(e):
    return "<h1>Page Not Found😢</h1>"

#============================================================================================================================
@app.route('/search',methods=['get'])
def search():
    query=request.args.get('q')
    tutorial_name=[]
    dict1={"course_fullname":query}
    tutorial_name.append(dict1)
    query=query.lower()
    stop_words=[]
    stopwords_file=open('/home/techbasics/mysite/techbasics/stopwords.txt','r')
    for line in stopwords_file.readlines():
        stop_words.append(line.strip())
    query_words=query.split(' ')
    for sw in stop_words:
        while(sw in query_words):
            query_words.remove(sw)

    results_set=[]
    for i in range(len(query_words)):
        for item in itertools.combinations(query_words,len(query_words)-i):
            like=""

            for qw in item:
                like=like+'like "%{tag}%" and tags '.format(tag=qw)

            like=like[0:-9]
            sql='select id from questions where tags '+like
            ques_ids=db.session.execute(sql)
            for row in ques_ids:
                results_set.append(row.id)
            exit=0;
            if len(results_set)>0:
                exit=1
                break
        if exit==1:
            break

    ques_id_tuple=tuple(set(results_set))
    questions=Questions.query.filter(Questions.id.in_(ques_id_tuple)).all()
    db.session.close()
    return render_template('/display-questions/index.html',questions=questions,tutorial_name=tutorial_name)

@app.route('/similarity')
def question_similarity():
    stop_words=[]
    stopwords_file=open('/home/techbasics/mysite/techbasics/stopwords.txt','r')
    for line in stopwords_file.readlines():
        stop_words.append(line.strip())
    questions=db.session.query(Questions.id,Questions.question)
    question_list=[]
    for row in questions:
        ques_id=row[0]
        ques_desc=row[1].lower()
        ques_words=ques_desc.split(' ');
        for sw in stop_words:
            while(sw in ques_words):
                ques_words.remove(sw)
        ques_word_list=[ques_id,ques_words]
        question_list.append(ques_word_list)

    vector=[]
    for i in question_list:
        for j in question_list:
            if len(i[1]) >= len(j[1]):
                matching_count=0
                for word1 in i[1]:
                    for word2 in j[1]:
                        if word1==word2:
                            matching_count=matching_count+1
                q1=[]
                q2=[]
                for x in range(len(i[1])):
                    q1.append(1)
                for y in range(len(i[1])):
                    if y<=matching_count:
                        q2.append(1)
                    else:
                        q2.append(0)
                cos_sim = dot(q1, q2)/(norm(q1)*norm(q2))
                cos_sim=float('{:.2f}'.format(cos_sim))
                data=[i[0],j[0],cos_sim]
                vector.append(data)
                #break;

            else:
                matching_count=0
                for word1 in j[1]:
                    for word2 in i[1]:
                        if word1==word2:
                            matching_count=matching_count+1
                q1=[]
                q2=[]
                for x in range(len(j[1])):
                    q2.append(1)
                for y in range(len(j[1])):
                    if y<=matching_count:
                        q1.append(1)
                    else:
                        q1.append(0)
                cos_sim = dot(q1, q2)/(norm(q1)*norm(q2))
                cos_sim=float('{:.2f}'.format(cos_sim))
                data=[i[0],j[0],cos_sim]
                vector.append(data)
    QuestionSimilarity.query.delete()
    for i in vector:
        ques_sim = QuestionSimilarity(i[0],i[1],i[2])
        db.session.add(ques_sim)
    db.session.commit()


    return 'Questions similarity updated'


@app.route('/rebuildtags')
def rebuid_tags():
    stop_words=[]
    stopwords_file=open('/home/techbasics/mysite/techbasics/stopwords.txt','r')
    for line in stopwords_file.readlines():
        stop_words.append(line.strip())
    result=db.session.query(Questions.id,Questions.question,Courses.course_fullname).filter(Questions.course_id==Courses.id).all()
    for rs in result:
        question=(rs.question).lower()
        course_name=(rs.course_fullname).lower()
        question_words=question.split(' ')
        course_words=course_name.split(' ')
        for sw in stop_words:
            while(sw in question_words): #small loop only
                question_words.remove(sw)

            while(sw in course_words):
                course_words.remove(sw) # very small loop
        join_ques_words='#'.join(question_words)
        join_ques_words=join_ques_words.replace('?','')
        join_ques_words=join_ques_words.replace('.','')
        join_ques_words=join_ques_words.replace(',','')
        join_course_words='_'.join(course_words)
        ques_tag='#'+join_course_words+'#'+join_ques_words
        Questions.query.filter((Questions.id==rs.id)).update({"tags":ques_tag})
    db.session.commit()
    return 'Question tags rebuilt'

@app.route('/roadmap')
def roadmap():
    return render_template('/roadmap/index.html')
@app.route('/projects')
def projects():
    return render_template('/projects/index.html')

#==============================MCQ ZONE=================
@app.route('/mcqzone')
def mcqzone():
    count=db.session.query(MCQ.id).count()
    return render_template('/mcq-zone/startquiz.html',count=count)

@app.route('/mcq-quiz')
def mcq_quiz():
    return render_template('/mcq-zone/mcqquiz.html')

@app.route('/fetchmcq',methods=['GET','POST'])
def fetch_mcq():
    if request.method == 'POST':
        content = request.get_json()
        mcq=db.session.query(MCQ.id,MCQ.question,MCQ.option1,MCQ.option2,MCQ.option3,MCQ.option4).filter(MCQ.question_type=='python').order_by(func.random()).all()
        return jsonify(mcq)
    else:
        return 'Access Denied'

@app.route('/score',methods=['GET','POST'])
def score():
    if request.method == 'POST':
        content = request.get_json()
        score=0
        total=db.session.query(MCQ.id).count()
        for str_dict in content:
            dict1 = json.loads(str_dict)
            question=db.session.query(MCQ.correct_option).filter(MCQ.id==int(dict1['question_id'])).all()
            if str(dict1['your_answer'])==str(question[0].correct_option):
                score=score+1;

        return 'Your score: '+str(score)+'/'+str(total)

    else:
        'no access'

@app.route('/loadmcq')
def loadmcq():
    df=pd.read_csv("/home/techbasics/question.csv")
    conn = sqlite3.connect('/home/techbasics/mysite/techbasics/site.db')
    db.session.execute("drop table mcq")
    db.session.commit()
    db.create_all()
    df.to_sql('mcq', conn,if_exists='append',index=False)
    return 'data loaded'








