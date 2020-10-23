from django.shortcuts import render
from django.http import JsonResponse
from polls.models import *
from polls.serializers import *
from collections import OrderedDict
import json

class bkdManager():
    def requestBKD(request, token, unit):
        user_token = Token.objects.filter(token = token)
        data = OrderedDict()
        if(user_token):
            unit = Unit.objects.filter(url_id = unit)
            if(unit):
                unit_bkd = UnitBKD.objects.get(unit = unit[0])
                bkd = BKD.objects.filter(id=unit_bkd.bkd.id)
                serializer = BKDIDSerializer(bkd,many=True)
                data["id"] = serializer.data[0]['url_id']
                data["visible"] = unit_bkd.opened
                data["title"] = bkd[0].title
                data["body"] = bkd[0].body

            else:
                data["message"] = 'Unit is not exist'
        else:
            data["message"] = 'Token is not exist'

        json.dumps(data, ensure_ascii=False, indent="\t")

        return JsonResponse(data, safe=False)

    def createBKD(request, token, unit):
        user_token = Token.objects.filter(token = token)
        data = OrderedDict()
        if(user_token):
            unit_one = Unit.objects.filter(url_id = unit)
            if(unit_one):    
                host = Host.objects.get(channel = unit_one[0].channel)
                if(user_token[0].user_id == host.user.id):
                    bkd = BKD.objects.create(title='', body='')
                    unit_bkd = UnitBKD.objects.create(bkd=bkd, unit=unit_one[0], opened=True)
                    bkd_owner = BKDOwner.objects.create(user=host.user, bkd=bkd)
                    bkd = BKD.objects.filter(id = bkd.id)
                    serializer = BKDIDSerializer(bkd,many=True)
                    data["id"] = serializer.data[0]['url_id']
                    data["visible"] = unit_bkd.opened
                    data["title"] = bkd[0].title
                    data["body"] = bkd[0].body

                else:
                    data["message"] = 'User is not channel\'s host'
            else:
                data["message"] = 'Unit is not exist'
        else:
            data["message"] = 'token is not exist'

        json.dumps(data, ensure_ascii=False, indent="\t")

        return JsonResponse(data, safe=False)

    def editBKD(request, token, bkd_id, visible, title, body):
        user_token = Token.objects.filter(token = token)
        data = OrderedDict()
        if(user_token):
            bkd = BKD.objects.filter(url_id = bkd_id)
            if(bkd):
                user = User.objects.get(id=user_token[0].user_id)
                bkd_owner = BKDOwner.objects.filter(user=user)
                if(bkd_owner):
                    bkd[0].opened = visible
                    bkd[0].title = title
                    bkd[0].body = body
                    bkd[0].save()

                    serializer = BKDIDSerializer(bkd,many=True)
                    data["id"] = serializer.data[0]['url_id']
                    data["visible"] = bkd[0].opened
                    data["title"] = bkd[0].title
                    data["body"] = bkd[0].body

                else:
                    data["message"] = 'User is not channel\'s host'
            else:
                data["message"] = 'BKD is not exist'
        else:
            data["message"] = 'token is not exist'

        json.dumps(data, ensure_ascii=False, indent="\t")

        return JsonResponse(data, safe=False)

    def deleteBKD(request, token, bkd_id):
        user_token = Token.objects.filter(token = token)
        data = OrderedDict()
        if(user_token):
            bkd = BKD.objects.filter(url_id = bkd_id)
            if(bkd):
                user = User.objects.get(id=user_token[0].user_id)
                bkd_owner = BKDOwner.objects.filter(user=user)
                if(bkd_owner):
                    bkd[0].delete()
                    bkd[0].save()
                    data["message"] = 'BKD is deleted'
                else:
                    data["message"] = 'User is not channel\'s host'
            else:
                data["message"] = 'BKD is not exist'
        else:
            data["message"] = 'Token is not exist'

        json.dumps(data, ensure_ascii=False, indent = "\t")

        return JsonResponse(data, safe=False)
