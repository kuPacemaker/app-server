from .ChannelJoinCodeGenerator.ChannelJoinCodeGenerator import channelJoinCodeGenerator
from django.http import JsonResponse
from polls.models import *
from polls.serializers import *
from collections import OrderedDict
import json

class hostChannel():
    def ChannelJoinCodeGenerate():
        joinCode = channelJoinCodeGenerator.channelJoinCodeGenerate() #생성된 채널코드

        return joinCode

#def excludeChannelMember():

    def createUnit(request, token, channel, index, title):
        user_token = Token.objects.filter(token = token)
        data = OrderedDict()
        if(user_token):
            #token 존재
            user_token = Token.objects.get(token = token)
            channel = Channel.objects.filter(url_id=channel)
            channel_serializer = ChannelInfoSerializer(channel,many=True)
            host = Host.objects.get(channel=channel[0])
            user = User.objects.filter(id=user_token.user_id)
            if(user == host.user):
                user = User.objects.get(id = host.id)
                unit = Unit.objects.create(channel = channel[0], index=index, name=title)
                unit_list = Unit.objects.filter(channel=channel[0]).order_by('index')
                unit_serializer = UnitSerializer(unit_list,many=True)
                unit_length = len(unit_list)       

                data["id"] = channel_serializer.data[0]['url_id']
                data["title"] = channel_serializer.data[0]['name']
                data["detail"] = channel_serializer.data[0]['description']
                data["leader"] = user.first_name
                data["code"] = channel_serializer.data[0]['accesspath']
                data["image"] = None
                data["units"] = [0 for i in range(unit_length)]
                for i in range(unit_length):
                    data["units"][i] = OrderedDict()
                    data["units"][i]["id"] = unit_serializer.data[i]['url_id']
                    data["units"][i]["index"] = unit_serializer.data[i]['index']
                    data["units"][i]["title"] = unit_serializer.data[i]['name']

                    data["units"][i]["state"] = OrderedDict()
                    data["units"][i]["state"]["hasDocument"] = False
                    data["units"][i]["state"]["hasPaper"] = False
                    data["units"][i]["state"]["startQuiz"] = False
                    data["units"][i]["state"]["endQuiz"] = False

            else:
                data["message"] = 'User is not this channel\'s host'

        else:
            #token 미존재
            data["message"] = 'Token is not exist'

        json.dumps(data, ensure_ascii=False, indent="\t")

        return JsonResponse(data, safe=False)

#def editUnit(request, token, cid, cname, cdesc):

    def deleteUnit(request, token, unit_id):
        user_token = Token.objects.filter(token = token)
        data = OrderedDict()
        if(user_token):
            #토큰 존재
            unit = Unit.objects.filter(url_id = unit_id)
            if(unit):
                host = Host.objects.filter(channel = unit[0].channel)
                if(user_token[0].user_id == host[0].user.id):
                    unit = Unit.objects.get(url_id = unit_id)
                    unit.delete()
                    data["message"] = 'Unit is deleted'

                else:
                    data["message"] = 'User is not this Channel\'s host'
            else:
                data["message"] = 'Unit is not exist'
        else:
            data["message"] = 'TOKEN IS NOT EXIST'

        json.dumps(data, ensure_ascii=False, indent="\t")

        return JsonResponse(data, safe=False)

#def registerBKD():

#def requestChapterList():

#def enterHostChannel():

#def browseHostChapter():

