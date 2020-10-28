from django.http import JsonResponse
from polls.models import *
from rest_framework.authtoken.models import Token
from polls.serializers import *
from polls.QGAPI.QGAPI import qgapi
from .HostChannel.ChannelJoinCodeGenerator.ChannelJoinCodeGenerator import channelJoinCodeGenerator
from collections import OrderedDict
from rest_framework.decorators import api_view
import json

class channelManager():
    def requestHostChannelList(token):
        user_token = Token.objects.filter(key = token)
        host_channel_list = []
        if(user_token):
            host_channel_id_list = []
            user_token = Token.objects.get(key = token)
            user = User.objects.get(id=user_token.user_id)
            host = Host.objects.filter(user=user)
            if(host):
                serializer = HostSerializer(host, many=True)
                length = len(serializer.data)
                print(length)
                for i in range(length):
                    host_channel_list += Channel.objects.filter(id=serializer.data[i]['channel'])
            else:
                print("HOST CHANNEL IS NOT EXIST")
        else:
            print("TOKEN IS NOT EXIST")
        
        return host_channel_list
        
    def requestGuestChannelList(token):
        user_token = Token.objects.filter(key = token)
        guest_channel_list = []
        if(user_token):
            guest_channel_id_list = []
            user_token = Token.objects.get(key = token)
            user = User.objects.get(id = user_token.user_id)
            guest = Guest.objects.filter(user = user)
            if(guest):
                serializer = GuestSerializer(guest, many=True)
                length = len(serializer.data)
                for i in range(length):
                    guest_channel_list += Channel.objects.filter(id=serializer.data[i]['channel'])
            else:
                print("GUEST CHANNEL IS NOT EXIST")
        else:
             print("TOKEN IS NOT EXIST")

        return guest_channel_list

    @api_view(['POST'])
    def createChannel(request):
        token = request.data['token']
        channel_name = request.data['channel_name']
        channel_desc = request.data['channel_desc']
        image = request.data['image']
        user_token = Token.objects.filter(key = token)
        data = OrderedDict()
        if(user_token):
            #token 존재
            user_token = Token.objects.get(key = token)
            user = User.objects.get(id = user_token.user_id)
            channel_join_code = channelJoinCodeGenerator.channelJoinCodeGenerate()
            host_channel_list = channelManager.requestHostChannelList(token)
            guest_channel_list = channelManager.requestGuestChannelList(token)
            host_length = len(host_channel_list)
            guest_length = len(guest_channel_list)
        
            data["state"] = "success"
            data["leader"] = [0 for i in range(host_length+1)]
            for i in range(host_length):
                #기존의 host channel list
                host_channel = Channel.objects.filter(id=host_channel_list[i].id)
                serializer = ChannelIDSerializer(host_channel, many=True)
                data["leader"][i] = OrderedDict()
                data["leader"][i]["id"] = serializer.data[0]['url_id']
                data["leader"][i]["title"] = host_channel_list[i].name
                data["leader"][i]["detail"] = host_channel_list[i].description
                data["leader"][i]["image"] = host_channel_list[i].image_type
                data["leader"][i]["leader_name"] = Host.objects.get(channel = host_channel_list[i]).user.first_name
               
            new_channel = Channel.objects.create(name=channel_name, description=channel_desc, accesspath=channel_join_code, image_type = image)
            Host.objects.create(channel = new_channel, user = user)
            Guest.objects.create(channel = new_channel, user = user)
            channel = Channel.objects.filter(id=new_channel.id)
            new_channel_serializer = ChannelInfoSerializer(channel,many=True)
            #새로 생성한 host channel list
            data["leader"][host_length] = OrderedDict()
            data["leader"][host_length]["id"] = new_channel_serializer.data[0]['url_id']
            data["leader"][host_length]["title"] = new_channel_serializer.data[0]['name']
            data["leader"][host_length]["detail"] = new_channel_serializer.data[0]['description']
            data["leader"][host_length]["image"] = new_channel_serializer.data[0]['image_type']
            data["leader"][host_length]["leader_name"] = user.first_name

            data["runner"] = [0 for i in range(guest_length+1)]
            for i in range(guest_length):
                guest_channel = Channel.objects.filter(id=guest_channel_list[i].id)
                serializer = ChannelIDSerializer(guest_channel,many=True)
                #UUID가 serializerable하도록 해주기 위해 url_id만 별도의 serailizer 사용
                data["runner"][i] = OrderedDict()
                data["runner"][i]["id"] = serializer.data[0]['url_id']
                data["runner"][i]["title"] = guest_channel_list[i].name
                data["runner"][i]["detail"] = guest_channel_list[i].description
                data["runner"][i]["image"] = guest_channel_list[i].image_type
                data["runner"][i]["leader_name"] = Host.objects.get(channel = guest_channel_list[i]).user.first_name
            
            #새로 생성한 guest channel list
            data["runner"][guest_length] = OrderedDict()
            data["runner"][guest_length]["id"] = new_channel_serializer.data[0]['url_id']
            data["runner"][guest_length]["title"] = new_channel_serializer.data[0]['name']
            data["runner"][guest_length]["detail"] = new_channel_serializer.data[0]['description']
            data["runner"][guest_length]["image"] = new_channel_serializer.data[0]['image_type']
            data["runner"][guest_length]["leader_name"] = user.first_name

        else:
            #token 미존재
            data["state"] = "fail"
            data["message"] = "Token is not exist"

        json.dumps(data, ensure_ascii=False, indent="\t")

        return JsonResponse(data, safe=False)

    @api_view(['POST'])
    def editChannel(request):
        token = request.data['token']
        channel_id = uuid.UUID(uuid.UUID(request.data['channel_id']).hex)
        channel_name = request.data['channel_name']
        channel_desc = request.data['channel_desc']
        user_token = Token.objects.filter(key = token)
        data = OrderedDict()
        if(user_token):
            #token 존재
            channel = Channel.objects.filter(url_id = channel_id)
            if(channel):
                #channel 존재
                host = Host.objects.filter(channel = channel[0])
                if(host.user.id == user_token[0].user_id):
                    channel = Channel.objects.get(url_id = channel_id)
                    if(channel_name != ""):
                        channel.name = channel_name
                    if(channel_desc != ""):
                        channel.description = channel_desc
                    channel.save()

                    data["state"] = "success"
                    channel = Channel.objects.filter(url_id = channel_id)
                    serializer = ChannelIDSerializer(channel, many=True)
                    data["id"] = serializer.data[0]['url_id']
                    data["title"] = channel[0].name
                    data["detail"] = channel[0].description
                    data["image"] = channel[0].image_type

                else:
                    #해당 채널이 user의 것이 아님
                    data["state"] = "fail"
                    data["message"] = "User is not channel\'s host"

            else:
                #channel 미존재
                data["state"] = "fail"
                data["message"] = "Channel is not exist"
            
        else:
            #token 미존재
            data["state"] = "fail"
            data["message"] = "Token is not exist"
        
        json.dumps(data, ensure_ascii=False, indent = "\t")

        return JsonResponse(data, safe=False)


    @api_view(['POST'])
    def deleteChannel(request):
        token = request.data['token']
        channel_id = uuid.UUID(uuid.UUID(request.data['channel_id']).hex)
        user_token = Token.objects.filter(key = token)
        data = OrderedDict()
        if(user_token):
            #token 존재
            channel = Channel.objects.filter(url_id = channel_id)
            if(channel):
                #channel 존재
                host = Host.objects.filter(channel = channel[0])
                if(host):
                    host[0].delete()
                    channel[0].delete()
                    data["state"] = "success"
                    data["message"] = "Channel is deleted."
                else:
                    data["state"] = "fail"
                    data["message"] = "User is not channel\'s host"
            else:
                #channel 미존재
                data["state"] = "fail"
                data["message"] = "Channel is not exist"
            
        else:
            #token 미존재
            data["state"] = "fail"
            data["message"] = "Token is not exist"

        json.dumps(data, ensure_ascii=False, indent="\t")

        return JsonResponse(data, safe=False)

    @api_view(['POST'])
    def requestChannel(request):
        token = request.data['token']
        channel_id = uuid.UUID(uuid.UUID(request.data['channel_id']).hex)
        user_token = Token.objects.filter(key = token)
        data = OrderedDict()
        if(user_token):
            #token 존재
            user = User.objects.get(id = user_token[0].user_id)
            channel = Channel.objects.filter(url_id = channel_id)
            if(channel):
                #channel 존재
                data["state"] = "success"
                serializer = ChannelIDSerializer(channel, many=True)
                data["id"] = serializer.data[0]['url_id']
                data["title"] = channel[0].name
                data["detail"] = channel[0].description
                data["code"] = channel[0].accesspath
                data["image"] = channel[0].image_type
                data["leader"] = Host.objects.get(channel = channel[0]).user.first_name

                guest = Guest.objects.filter(channel = channel[0])
                guest_length = len(guest)
                if(guest_length != 0):
                    data["runners"] = [0 for i in range(guest_length)]
                    for i in range(guest_length):
                        data["runners"][i] = guest[i].user.first_name
                else:
                     data["runners"] = []
                unit = Unit.objects.filter(channel = channel[0]).order_by('index')
                if(unit.count() != 0):
                    unit_serializer = UnitSerializer(unit, many=True)
                    data["units"] = [0 for i in range(unit.count())]
                    for i in range(unit.count()):
                        data["units"][i] = OrderedDict()
                        data["units"][i]["id"] = unit_serializer.data[i]['url_id']
                        data["units"][i]["index"] = unit_serializer.data[i]['index']
                        data["units"][i]["title"] = unit_serializer.data[i]['name']
                        data["units"][i]["state"] = OrderedDict()
                        data["units"][i]["state"]["hasDocument"] = UnitBKD.objects.filter(unit = unit[i]).exists()
                        data["units"][i]["state"]["hasPaper"] = UnitQA.objects.filter(unit = unit[i]).exists()
                        test = UnitTest.objects.filter(unit = unit[i])
                        if(test.exists()):
                            startQuiz = test[0].test.released
                            testset = TestSet.objects.filter(user = user, test = test[0].test)
                            if(testset.exists()):
                                endQuiz = testset[0].submitted
                            else:
                                endQuiz = False
                        else:
                            startQuiz = False
                            endQuiz = False
                        data["units"][i]["state"]["startQuiz"] = startQuiz
                        data["units"][i]["state"]["endQuiz"] = endQuiz
                else:
                     data["units"] = []
            else:
                 data["state"] = "fail"
                 data["message"] = "Channel is not exist"
        else:
             data["state"] = "fail"
             data["message"] = "Token is not exist"

        json.dumps(data, ensure_ascii=False, indent="\t")

        return JsonResponse(data, safe=False)

    @api_view(['POST'])
    def requestUnit(request):
        token = request.data['token']
        unit_id = uuid.UUID(uuid.UUID(request.data['unit_id']).hex)
        data = OrderedDict()

        user_token = Token.objects.filter(key = token)
        unit = Unit.objects.filter(url_id = unit_id)
        if not (user_token.exists()):
            data["state"] = "fail"
            data["message"] = "Token is not exist"
        elif not (unit.exists()):
            data["state"] = "fail"
            data["message"] = "Unit is not exist"
        else:
            user = User.objects.get(id = user_token[0].user_id)
            hosts = Host.objects.filter(user = user, channel = unit[0].channel)
            guests = Guest.objects.filter(user = user, channel = unit[0].channel)
            if not (hosts.exists() or guests.exists()):
                data["state"] = "fail"
                data["message"] = "User is neither host nor guest of Channel"

        if bool(data):
            json.dumps(data, ensure_ascii=False, indent="\t")
            return JsonResponse(data, safe=False)

        user = User.objects.get(id = user_token[0].user_id)
        unit = Unit.objects.filter(url_id = unit_id)
        channel = Channel.objects.filter(id = unit[0].channel.id)

        data["state"] = "success"
        serializer = ChannelInfoSerializer(channel, many=True)
        data["channel"] = OrderedDict()
        data["channel"]["id"] = serializer.data[0]['url_id']
        data["channel"]["title"] = serializer.data[0]['name']
        data["channel"]["detail"] = serializer.data[0]['description']
        data["channel"]["code"] = serializer.data[0]['accesspath']

        serializer = UnitSerializer(unit, many=True)
        data["unit"] = OrderedDict()
        data["unit"]["id"] = serializer.data[0]['url_id']
        data["unit"]["index"] = serializer.data[0]['index']
        data["unit"]["title"] = serializer.data[0]['name']
        data["unit"]["isOpened"] = True

        unit_bkd = UnitBKD.objects.filter(unit = unit[0])
        data["unit"]["document"] = OrderedDict()
        if (unit_bkd):
            bkd = BKD.objects.filter(id = unit_bkd[0].bkd.id)
            serializer = BKDSerializer(bkd, many=True)
            data["unit"]["document"]["id"] = serializer.data[0]['url_id']
            data["unit"]["document"]["visible"] = unit_bkd[0].opened
            data["unit"]["document"]["title"] = bkd[0].title
            data["unit"]["document"]["body"] = bkd[0].body
        else:
            data["unit"]["document"]["id"] = None
            data["unit"]["document"]["visible"] = False
            data["unit"]["document"]["title"] = ""
            data["unit"]["document"]["body"] = ""

        data["paper"] = OrderedDict()
        if (UnitQA.objects.filter(unit = unit[0]).exists()):
            qaset = UnitQA.objects.get(unit = unit[0]).qaset

            if (UnitTest.objects.filter(unit = unit[0]).exists()):
                test = UnitTest.objects.get(unit = unit[0]).test
                data["paper"]["isStart"] = test.released
                data["paper"]["isEnd"] = test.ended
            else:
                data["paper"]["isStart"] = None
                data["paper"]["isEnd"] = None

            qapairs = QAPair.objects.filter(qaset = qaset)
            qapair_length = qapairs.count()
            serializer = QAPairSerializer(qapairs, many=True)
            if(qapair_length != 0):
                data["paper"]["questions"] = [0 for i in range(qapair_length)]
                for i in range(qapair_length):
                    data["paper"]["questions"][i] = OrderedDict()
                    data["paper"]["questions"][i]["id"] = serializer.data[i]['url_id']
                    data["paper"]["questions"][i]["quiz"] = qapairs[i].question
                    data["paper"]["questions"][i]["answer"] = qapairs[i].answer
                    data["paper"]["questions"][i]["user_answer"] = ''
                    data["paper"]["questions"][i]["answer_set"] = qgapi.stringWithSlash(qapairs[i].answer_set)
                    data["paper"]["questions"][i]["verified"] = True
            else:
                 data["paper"]["questions"] = []

        else:
            data["paper"]["isStart"] = False
            data["paper"]["isEnd"] = False
            data["paper"]["questions"] = []

        json.dumps(data, ensure_ascii=False, indent="\t")

        return JsonResponse(data, safe=False)

    @api_view(['POST'])
    def requestBoard(request):
        token = request.data['token']
        data = OrderedDict()

        user_token = Token.objects.filter(key = token)
        if not (user_token.exists()):
            data["state"] = "fail"
            data["message"] = "Token is not exist"

        if bool(data):
            json.dumps(data, ensure_ascii=False, indent="\t")
            return JsonResponse(data, safe=False)

        data["state"] = "success"

        user = User.objects.get(id = user_token[0].user_id)

        hosts = Host.objects.filter(user = user)
        host_channel = Channel.objects.filter(id__in = hosts.values_list('channel', flat=True))
        host_length = host_channel.count()
        serializer = ChannelInfoSerializer(host_channel, many=True)
        data["leader"] = [0 for i in range(host_length)]
        for i in range(host_length):
            data["leader"][i] = OrderedDict()
            data["leader"][i]["id"] = serializer.data[i]['url_id']
            data["leader"][i]["title"] = serializer.data[i]['name']
            data["leader"][i]["detail"] = serializer.data[i]['description']
            data["leader"][i]["image"] = serializer.data[i]['image_type']

        guests = Guest.objects.filter(user = user)
        guest_channel = Channel.objects.filter(id__in = guests.values_list('channel', flat=True))
        guest_length = guest_channel.count()
        serializer = ChannelInfoSerializer(guest_channel, many=True)
        data["runner"] = [0 for i in range(guest_length)]
        for i in range(guest_length):
            data["runner"][i] = OrderedDict()
            data["runner"][i]["id"] = serializer.data[i]['url_id']
            data["runner"][i]["title"] = serializer.data[i]['name']
            data["runner"][i]["detail"] = serializer.data[i]['description']
            data["runner"][i]["image"] = serializer.data[i]['image_type']

        json.dumps(data, ensure_ascii=False, indent="\t")

        return JsonResponse(data, safe=False)
