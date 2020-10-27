from django.shortcuts import render
from django.http import JsonResponse
from polls.models import *
from polls.serializers import *
from collections import OrderedDict
from rest_framework.decorators import api_view
import json, uuid

class bkdManager():
    @api_view(['POST'])
    def requestBKD(request):
        token = request.data['token']
        unit_id = uuid.UUID(uuid.UUID(request.data['unit_id']).hex)
        user_token = Token.objects.filter(key = token)
        data = OrderedDict()
        if(user_token):
            unit = Unit.objects.filter(url_id = unit_id)
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

    @api_view(['POST'])
    def createBKD(request):
        token = request.data['token']
        unit_id = uuid.UUID(uuid.UUID(request.data['unit_id']).hex)
        user_token = Token.objects.filter(key = token)
        data = OrderedDict()
        if(user_token):
            unit = Unit.objects.filter(url_id = unit_id)
            if(unit):    
                host = Host.objects.get(channel = unit[0].channel)
                if(user_token[0].user_id == host.user.id):
                    bkd = BKD.objects.create(title='', body='')
                    unit_bkd = UnitBKD.objects.create(bkd=bkd, unit=unit[0], opened=True)
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

    @api_view(['POST'])
    def editBKD(request):
        token = request.data['token']
        bkd_id = uuid.UUID(uuid.UUID(request.data['bkd_id']).hex)
        visible = request.data['visible']
        title = request.data['title']
        body = request.data['body']
        user_token = Token.objects.filter(key = token)
        data = OrderedDict()
        if(user_token):
            bkd = BKD.objects.filter(url_id = bkd_id)
            if(bkd):
                user = User.objects.get(id=user_token[0].user_id)
                bkd_owner = BKDOwner.objects.filter(user=user)
                if(bkd_owner):
                    if(visible != ""):
                        bkd[0].opened = visible
                    if(title != ""):
                        bkd[0].title = title
                    if(body != ""):
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

    @api_view(['POST'])
    def deleteBKD(request):
        token = request.data['token']
        bkd_id = uuid.UUID(uuid.UUID(request.data['bkd_id']).hex)
        user_token = Token.objects.filter(key = token)
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
