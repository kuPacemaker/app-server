from django.shortcuts import render
from django.http import JsonResponse
from ..models import Question, User
from .EmailSender.EmailSender import emailSender
from rest_framework.authtoken.models import Token
from ..serializers import TokenSerializer, UserSerializer
import json
from collections import OrderedDict

class accountManager():
    def signIn(request,uid,pw):
        user = User.objects.filter(username = uid)
        data = OrderedDict()
        if(user):
            user = User.objects.get(username = uid)
            #DB에 저장된 email이 uid와 일치함
            if(user.password == pw):
                #DB에 저장된 email과 쌍을 이루는 password가 upw와 일치함
                print("LOGIN SUCCESS")
                
                token = Token.objects.filter(user_id = user.id)
                serializer = TokenSerializer(token, many=True)

                data["id"] = user.username
                data["name"] = user.first_name
                data["type"] = None
                data["token"] = serializer.data[0]['token']
            else:
                #password와 upw가 일치하지 않음
                print("PASSWORD WRONG")
                data["id"] = None
                data["name"] = None
                data["type"] = None
                data["token"] = None
        else:
            #DB에 email이 존재하지 않음
            print("EMAIL WRONG")
            data["id"] = None
            data["name"] = None
            data["type"] = None
            data["token"] = None

        json.dumps(data, ensure_ascii=False, indent="\t")

        return JsonResponse(data, safe=False)

    def signUp(request,uid,name,pw):
        user = User.objects.filter(username = id)
        data = OrderedDict()
        if(user):
            #DB에 uid가 이미 존재함
            print("EMAIL EXIST")
            data["message"] = "Fail. Email is already exist."
        else:        
            #존재하지 않으므로 사용 가능함
            user = User.objects.create(username = uid, password = pw, first_name = name)
            data["message"] = "Success."

        json.dumps(data, ensure_ascii=False, indent="\t")

        return JsonResponse(data, safe=False)

    def findAccount(request,uid):
        #user의 first_name도 같이 포함해서 찾아야 함
        user = User.objects.filter(username = uid)
        data = OrderedDict()
        if(user):
            user= User.objects.get(username = uid)
            new_password = emailSender.sendEmail(uid) #반환값을 DB에 저장할 목적
            user.password = new_password
            user.save()
            data["message"] = "Success. E-Mail sended."
        else:
            #DB에 email과 일치하는 uid가 없음
            print("EMAIL IS NOT EXIST")
            data["message"] = "Fail. E-Mail is not exist."

        json.dumps(data, ensure_ascii=False, indent="\t")

        return JsonResponse(data, safe=False)

    def modifyAccount(request,uid,name,pw,pw_new):
        #토큰도 입력으로 받아야 한다.
        user = User.objects.get(username = uid)
        data = OrderedDict()
        if(user.password == pw):
            #DB의 기존 비밀번호와 사용자 입력이 일치
            user.password = pw_new
            user.first_name = name
            user.save()
            data["message"] = "Success."
        else:
            #불일치
            print("PASSWORD IS WRONG")
            data["message"] = "Fail. Password is wrong."

        json.dumps(data, ensure_ascii = False, indent = "\t")

        return JsonResponse(data, safe=False)
