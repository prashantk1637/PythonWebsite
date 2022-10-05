from techbasics import db
from datetime import datetime
from dateutil.tz import gettz
db.create_all()
##DB Models ==
class Users(db.Model):

    __tablename__='users'
    email = db.Column(db.String(20),primary_key = True)
    password = db.Column(db.String(50))
    type=db.Column(db.String(10))
    name=db.Column(db.String(20))
    is_active=db.Column(db.String(3))
    def __init__(self,email,password,name):
       self.email = email
       self.password = password
       self.name = name
       self.type='normal'
       self.is_active='no'

class Posts(db.Model):
    __tablename__='posts'
    id = db.Column(db.Integer, primary_key = True)
    post = db.Column(db.String(500))
    time = db.Column(db.String(20))
    name= db.Column(db.String(20))

    def __init__(self,post,name="Anonymous"):
       self.post = post
       dtobj = datetime.now(tz=gettz('Asia/Calcutta'))
       t=dtobj.strftime("%b %d %Y %H:%M")
       self.time =t
       self.name = name
class Courses(db.Model):
    __tablename__='courses'
    id = db.Column(db.Integer, primary_key = True)
    course_fullname = db.Column(db.String(100))

    def __init__(self,course_name):
       self.course_fullname = course_name

class Questions(db.Model):
    __tablename__='questions'
    id = db.Column(db.Integer, primary_key = True)
    question = db.Column(db.String(100))
    answer = db.Column(db.String(500))
    course_id=db.Column(db.Integer)
    tags= db.Column(db.String(100))

    def __init__(self,question,answer,course_id,tags):
       self.question = question
       self.answer =answer
       self.course_id = course_id
       self.tags=tags

class MCQ(db.Model):
    __tablename__='mcq'
    id = db.Column(db.Integer, primary_key = True)
    question = db.Column(db.String(100))
    question_type = db.Column(db.String(20))
    option1 = db.Column(db.String(100))
    option2 = db.Column(db.String(100))
    option3 = db.Column(db.String(100))
    option4 = db.Column(db.String(100))
    correct_option = db.Column(db.String(100))

    def __init__(self,question,option1,option2,option3,option4,correct_option):
       self.question = question
       self.option1 =option1
       self.option2 =option2
       self.option3 =option3
       self.option4 =option4
       self.correct_option =correct_option


class PageVisitors(db.Model):
    __tablename__='pagevisitors'
    id = db.Column(db.Integer, primary_key = True)
    remote_ip = db.Column(db.String(20))
    visit_time = db.Column(db.String(20))
    visit_count = db.Column(db.Integer,default=0)

    def __init__(self,remote_ip,count):
       self.remote_ip = remote_ip
       dtobj = datetime.now(tz=gettz('Asia/Calcutta'))
       time=dtobj.strftime("%b %d %Y")
       self.visit_time =time #storing date without time to calculate daily visits
       self.visit_count=count

class QuestionSimilarity(db.Model):
    __tablename__='questionsimilarity'
    id = db.Column(db.Integer, primary_key = True)
    ques_id1=db.Column(db.Integer)
    ques_id2=db.Column(db.Integer)
    simiarity= db.Column(db.Float)

    def __init__(self,ques_id1,ques_id2,simiarity):
       self.ques_id1=ques_id1
       self.ques_id2=ques_id2
       self.simiarity=simiarity


