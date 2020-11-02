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
        uid = request.data['id']
        pw = request.data['pw']
        user_list = User.objects.all()
        user = None
        for i in range(user_list.count()):
            if(cipher.decrypt(user_list[i].username) == uid):
                user = user_list[i]
                break
        data = OrderedDict()
        if(user):
            #DB에 저장된 email이 uid와 일치함
            if(cipher.decrypt(user.password) == pw):
                #DB에 저장된 email과 쌍을 이루는 password가 upw와 일치함                
                past_token = Token.objects.get(user_id = user.id)
                past_token.delete()
                Token.objects.create(user = user)
                token = Token.objects.filter(user_id = user.id)
                serializer = TokenSerializer(token, many=True)

                data["state"] = "success"
                data["id"] = cipher.decrypt(user.username)
                data["name"] = cipher.decrypt(user.first_name)
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
        uid = request.data['id']
        name = cipher.encrypt(request.data['name'])
        pw = cipher.encrypt(request.data['pw'])
        user = None
        user_list = User.objects.all()
        for i in range(user_list.count()):
            if(cipher.decrypt(user_list[i].username) == uid):
                user = user_list[i]
                break
        data = OrderedDict()
        if(user):
            #DB에 uid가 이미 존재함
            data["state"] = "fail"
            data["message"] = "ID is already exist."
        else:        
            #존재하지 않으므로 사용 가능함
            user = User.objects.create(username = cipher.encrypt(uid), password = pw, first_name = name)
            data["state"] = "success"
            data["message"] = "Sign up completed."

        json.dumps(data, ensure_ascii=False, indent="\t")

        return JsonResponse(data, safe=False)

    @api_view(['POST'])
    def findAccount(request):
        cipher = AESCipher()
        uid = request.data['id']
        #user의 first_name도 같이 포함해서 찾아야 함
        user = None
        user_list = User.objects.all()
        for i in range(user_list.count()):
            if(cipher.decrypt(user_list[i].username) == uid):
                user = user_list[i]
                break
        data = OrderedDict()
        if(user):
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
        uid = request.data['id']
        name = request.data['name']
        pw = request.data['pw']
        pw_new = request.data['pw_new']
        user_token = Token.objects.filter(key = token)
        data = OrderedDict()
        if(user_token):
            user_list = User.objects.all()
            user = None
            for i in range(user_list.count()):
                if(cipher.decrypt(user_list[i].username) == uid):
                    user = user_list[i]
                    break
            if(user):
                if(cipher.decrypt(user.password) == pw):
                    if(name != ""):
                        user.first_name = cipher.encrypt(name)
                    if(pw_new != ""):
                        user.password = cipher.encrypt(pw_new)
                    user.save()
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
