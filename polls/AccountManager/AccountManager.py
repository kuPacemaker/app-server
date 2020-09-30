from django.shortcuts import render
from ..models import Question, User
from .EmailSender.EmailSender import emailSender
from rest_framework.authtoken.models import Token

class accountManager():
    def login(request,uid,upw):
        user = User.objects.filter(username = uid)
        if(user):
            user = User.objects.get(username = uid)
            #DB에 저장된 email이 uid와 일치함
            if(user.password == upw):
                #DB에 저장된 email과 쌍을 이루는 password가 upw와 일치함
                print("LOGIN SUCCESS")
                token = Token.objects.get(user_id = user.id)
                print("token :",token)
            else:
                #password와 upw가 일치하지 않음
                print("PASSWORD WRONG")
        else:
            #DB에 email이 존재하지 않음
            print("EMAIL WRONG")

        latest_question_list = Question.objects.order_by('-pub_date')[:5]
        context = {'latest_question_list':latest_question_list}
        return render(request, 'polls/index.html',context)

    def signIn(request,uid,upw,uname):
        user = User.objects.filter(username = uid)
        if(user):
            #DB에 uid가 이미 존재함
            print("EMAIL EXIST")
        else:        
            #존재하지 않으므로 사용 가능함
            user = User.objects.create(username = uid, password = upw, first_name = uname)
            print("SIGN_IN SUCCESS")
            token = Token.objects.get(user_id = user.id)
            print("token :",token)

        latest_question_list = Question.objects.order_by('-pub_date')[:5]
        context = {'latest_question_list':latest_question_list}
        return render(request, 'polls/index.html',context)

    def findAccount(request,uid):
        user = User.objects.filter(username = uid)
        if(user):
            user= User.objects.get(username = uid)
            new_password = emailSender.sendEmail(uid) #반환값을 DB에 저장할 목적
            user.password = new_password
            user.save()
        else:
            #DB에 email과 일치하는 uid가 없음
            print("EMAIL IS NOT EXIST")

        latest_question_list = Question.objects.order_by('-pub_date')[:5]
        context = {'latest_question_list':latest_question_list}
        return render(request, 'polls/index.html',context)

    def modifyAccountInfo(request,uid,uname,upw,newpw):
        user = User.objects.get(username = uid)
        if(user.password == upw):
            #DB의 기존 비밀번호와 사용자 입력이 일치
            user.password = newpw
            user.first_name = uname

            user.save()
        else:
            #불일치
            print("PASSWORD IS WRONG")

        latest_question_list = Question.objects.order_by('-pub_date')[:5]
        context = {'latest_question_list':latest_question_list}
        return render(request, 'polls/index.html',context)
