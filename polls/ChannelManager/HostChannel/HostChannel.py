from .ChannelJoinCodeGenerator.ChannelJoinCodeGenerator import channelJoinCodeGenerator
from django.http import JsonResponse
from polls.models import *
from polls.serializers import *
from collections import OrderedDict
from rest_framework.decorators import api_view
import json, uuid

class hostChannel():
    def ChannelJoinCodeGenerate():
        joinCode = channelJoinCodeGenerator.channelJoinCodeGenerate() #생성된 채널코드

        return joinCode

#def excludeChannelMember():

    @api_view(['POST'])
    def createUnit(request):
        token = request.data['token']
        channel_id = uuid.UUID(uuid.UUID(request.data['channel_id']).hex)
        index = request.data['index']
        title = request.data['title']
        user_token = Token.objects.filter(key = token)
        data = OrderedDict()
        if(user_token):
            #token 존재
            user_token = Token.objects.get(key = token)
            channel = Channel.objects.filter(url_id=channel_id)
            channel_serializer = ChannelInfoSerializer(channel,many=True)
            host = Host.objects.get(channel=channel[0])
            user = User.objects.filter(id=user_token.user_id)
            if(user[0] == host.user):
                unit = Unit.objects.create(channel = channel[0], index=index, name=title)
                unit_list = Unit.objects.filter(channel=channel[0]).order_by('index')
                unit_serializer = UnitSerializer(unit_list,many=True)
                unit_length = len(unit_list)       

                data["state"] = "success"
                data["id"] = channel_serializer.data[0]['url_id']
                data["title"] = channel_serializer.data[0]['name']
                data["detail"] = channel_serializer.data[0]['description']
                data["leader"] = user[0].first_name
                data["code"] = channel_serializer.data[0]['accesspath']
                data["image"] = channel_serializer.data[0]['image_type']
                data["units"] = [0 for i in range(unit_length)]
                for i in range(unit_length):
                    data["units"][i] = OrderedDict()
                    data["units"][i]["id"] = unit_serializer.data[i]['url_id']
                    data["units"][i]["index"] = unit_serializer.data[i]['index']
                    data["units"][i]["title"] = unit_serializer.data[i]['name']

                    data["units"][i]["state"] = OrderedDict()
                    data["units"][i]["state"]["hasDocument"] = UnitBKD.objects.filter(unit = unit_list[i]).exists()
                    data["units"][i]["state"]["hasPaper"] = UnitQA.objects.filter(unit = unit_list[i]).exists()
                    data["units"][i]["state"]["startQuiz"] = False
                    data["units"][i]["state"]["endQuiz"] = False

                guest = Guest.objects.filter(channel = channel[0])
                guest_length = len(guest)
                if(guest_length != 0):
                    data["runners"] = [0 for i in range(guest_length)]
                    for i in range(guest_length):
                        data["runners"][i] = guest[i].user.first_name
                else:
                     data["runners"] = []

            else:
                data["state"] = "fail"
                data["message"] = "User is not this channel\'s host"

        else:
            #token 미존재
            data["state"] = "fail"
            data["message"] = "Token is not exist"

        json.dumps(data, ensure_ascii=False, indent="\t")

        return JsonResponse(data, safe=False)

    @api_view(['POST'])
    def editUnit(request):
        token = request.data['token']
        unit_id = uuid.UUID(uuid.UUID(request.data['unit_id']).hex)
        index = request.data['index']
        title = request.data['title']
        user_token = Token.objects.filter(key = token)
        data = OrderedDict()
        if(user_token):
            #토큰 존재
            unit = Unit.objects.filter(url_id = unit_id)
            if(unit):
                host = Host.objects.filter(channel = unit[0].channel)
                if(user_token[0].user_id == host[0].user.id):
                    exist_unit = Unit.objects.filter(channel = unit[0].channel, index = index)
                    unit = Unit.objects.get(url_id = unit_id)
                    if(not exist_unit):
                        unit.index = index
                    if(title != ""):
                        unit.name = title
                    unit.save()

                    data["state"] = "success"
                    unit = Unit.objects.filter(url_id = unit_id)
                    serializer = UnitSerializer(unit, many=True)
                    data["id"] = serializer.data[0]['url_id']
                    data["index"] = unit[0].index
                    data["title"] = unit[0].name
                else:
                    data["state"] = "fail"
                    data["message"] = "User is not channel\'s host"
            else:
                data["state"] = "fail"
                data["message"] = "Unit is not exist"
        else:
            data["state"] = "fail"
            data["message"] = "Token is not exist"

        json.dumps(data, ensure_ascii=False, indent="\t")

        return JsonResponse(data, safe=False)

    @api_view(['POST'])
    def deleteUnit(request):
        token = request.data['token']
        unit_id = uuid.UUID(uuid.UUID(request.data['unit_id']).hex)
        user_token = Token.objects.filter(key = token)
        data = OrderedDict()
        if(user_token):
            #토큰 존재
            unit = Unit.objects.filter(url_id = unit_id)
            if(unit):
                host = Host.objects.filter(channel = unit[0].channel)
                if(user_token[0].user_id == host[0].user.id):
                    unit = Unit.objects.get(url_id = unit_id)
                    unit.delete()
                    data["state"] = "success"
                    data["message"] = "Unit is deleted."

                else:
                    data["state"] = "fail"
                    data["message"] = "User is not this Channel\'s host"
            else:
                data["state"] = "fail"
                data["message"] = "Unit is not exist"
        else:
            data["state"] = "fail"
            data["message"] = "Token is not exist"

        json.dumps(data, ensure_ascii=False, indent="\t")

        return JsonResponse(data, safe=False)

#def registerBKD():

#def requestChapterList():

#def enterHostChannel():

#def browseHostChapter():

