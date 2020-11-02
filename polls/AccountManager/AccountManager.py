from django.shortcuts import render
from django.http import JsonResponse
from polls.models import *
from .EmailSender.EmailSender import emailSender
#from rest_framework.authtoken.models import Token
from polls.serializers import *
from rest_framework.decorators import api_view
from collections import OrderedDict
from polls.AESCipher import AESCipher
import json

class accountManager():
    @api_view(['POST'])
    def signIn(request):
        cipher = AESCipher()
        uid = cipher.encrypt(request.data['id'])
        pw = cipher.encrypt(request.data['pw'])
        print(uid,pw)
        user = User.objects.filter(username = uid)
        data = OrderedDict()
        if(user):
            user = User.objects.get(username = uid)
            #DB에 저장된 email이 uid와 일치함
            if(user.password == pw):
                #DB에 저장된 email과 쌍을 이루는 password가 upw와 일치함                
                past_token = Token.objects.get(user_id = user.id)
                past_token.delete()
                Token.objects.create(user = user)
                token = Token.objects.filter(user_id = user.id)
                serializer = TokenSerializer(token, many=True)

                data["state"] = "success"
                data["id"] = cipher.decrypt(user.username)
                data["name"] = cpher.decrypt(user.first_name)
                data["type"] = "Standard"
                data["token"] = serializer.data[0]['key']
            else:
                #password와 upw가 일치하지 않음
                data["state"] = "fail"
                data["message"] = "Password is wrong."
        else:
            #DB에 email이 존재하지 않음
            data["state"] = "fail"
            data["message"] = "ID is not exist."

        json.dumps(data, ensure_ascii=False, indent="\t")

        return JsonResponse(data, safe=False)

    @api_view(['POST'])
    def signUp(request):
        cipher = AESCipher()
        uid = cipher.encrypt(request.data['id'])
        name = cipher.encrypt(request.data['name'])
        pw = cipher.encrypt(request.data['pw'])
        user = User.objects.filter(username = uid)
        data = OrderedDict()
        if(user):
            #DB에 uid가 이미 존재함
            data["state"] = "fail"
            data["message"] = "ID is already exist."
        else:        
            #존재하지 않으므로 사용 가능함
            user = User.objects.create(username = uid, password = pw, first_name = name)
            data["state"] = "success"
            data["message"] = "Sign up completed."

        json.dumps(data, ensure_ascii=False, indent="\t")

        return JsonResponse(data, safe=False)

    @api_view(['POST'])
    def findAccount(request):
        cipher = AESCipher()
        uid = cipher.encrypt(request.data['id'])
        #user의 first_name도 같이 포함해서 찾아야 함
        user = User.objects.filter(username = uid)
        data = OrderedDict()
        if(user):
            user= User.objects.get(username = uid)
            new_password = emailSender.sendEmail(uid) #반환값을 DB에 저장할 목적
            user.password = cipher.encrypt(new_password)
            user.save()
            data["state"] = "success"
            data["message"] = "E-Mail sended."
        else:
            #DB에 email과 일치하는 uid가 없음
            data["state"] = "fail"
            data["message"] = "E-Mail is not exist."

        json.dumps(data, ensure_ascii=False, indent="\t")

        return JsonResponse(data, safe=False)

    @api_view(['POST']) 
    def modifyAccount(request):
        cipher = AESCipher()
        token = request.data['token']
        uid = cipher.encrypt(request.data['id'])
        name = cipher.encrypt(request.data['name'])
        pw = cipher.encrypt(request.data['pw'])
        pw_new = cipher.encrypt(request.data['pw_new'])
        user_token = Token.objects.filter(key = token)
        data = OrderedDict()
        if(user_token):
            user = User.objects.filter(username=uid)
            if(user):
                if(user[0].password == pw):
                    if(name != ""):
                        user[0].first_name = name
                    if(pw_new != ""):
                        user[0].password = pw_new
                    user[0].save()
                    data["state"] = "success"
                    data["message"] = "Save completed."
                else:
                    data["state"] = "fail"
                    data["message"] = 'Password is wrong'
            else:
                data["state"] = "fail"
                data["message"] = "E-mail is not exist"
        else:
            data["state"] = "fail"
            data["message"] = "Token is not exist"

        json.dumps(data, ensure_ascii = False, indent = "\t")

        return JsonResponse(data, safe=False)
