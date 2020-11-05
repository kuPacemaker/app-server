from django.http import JsonResponse
from polls.models import *
from polls.serializers import *
from collections import OrderedDict
from ..ChannelManager import channelManager
from rest_framework.decorators import api_view
import json

class guestChannel():
    @api_view(['POST'])
    def enterChannel(request):
        token = request.data['token']
        accesscode = request.data['accesscode']
        user_token = Token.objects.filter(key = token)
        channel = Channel.objects.filter(accesspath = accesscode)
        data = OrderedDict()
        if(user_token):
            if(not channel):
                #입장코드와 일치하는 채널이 존재하지 않음
                data["state"] = "fail"
                data["message"] = "Channel is not exist"
            else:
                user_token = Token.objects.get(key = token)
                user = User.objects.get(id = user_token.user_id)
                host = Host.objects.filter(user=user,channel = channel[0])
                if(host):
                    #호스트가 자기자신의 채널로 입장을 시도하면 입장불가
                    data["state"] = "fail"
                    data["message"] = "Host cannot enter their own channel"
                else:
                    guest = Guest.objects.filter(user = user, channel = channel[0])
                    if(guest.exists()):
                        #이미 게스트로 입장한 채널이므로 재입장 불가
                        data["state"] = "fail"
                        data["message"] = "You are already guest in this channel"
                    else:
                        Guest.objects.create(user = user, channel = channel[0])

                        host_channel_list = channelManager.requestHostChannelList(token)
                        guest_channel_list = channelManager.requestGuestChannelList(token)
                        host_length = len(host_channel_list)
                        guest_length = len(guest_channel_list)
        
                        data["state"] = "success"
                        data["message"] = "Enter the channel completed"
                        if(host_length != 0):
                            data["leader"] = [0 for i in range(host_length)]
                            for i in range(host_length):
                                host_channel = Channel.objects.filter(id=host_channel_list[i].id)
                                serializer = ChannelIDSerializer(host_channel,many=True)
                                data["leader"][i] = OrderedDict()
                                data["leader"][i]["id"] = serializer.data[0]['url_id']
                                data["leader"][i]["title"] = host_channel_list[i].name
                                data["leader"][i]["detail"] = host_channel_list[i].description
                                data["leader"][i]["image"] = host_channel_list[i].image_type
                        else:
                            data["leader"] = []

                        data["runner"] = [0 for i in range(guest_length)]
                        for i in range(guest_length):
                            guest_channel = Channel.objects.filter(id=guest_channel_list[i].id)
                            serializer = ChannelIDSerializer(guest_channel,many=True)
                            #UUID가 serializable하도록 해주기 위해 url_id만 별도의 serializer를 돌림
                            data["runner"][i] = OrderedDict()
                            data["runner"][i]["id"] = serializer.data[0]['url_id']
                            data["runner"][i]["title"] = guest_channel_list[i].name
                            data["runner"][i]["detail"] = guest_channel_list[i].description
                            data["runner"][i]["image"] = guest_channel_list[i].image_type
            
        else:
            data["state"] = "fail"
            data["message"] = "Token is not exist"

        json.dumps(data, ensure_ascii=False, indent="\t")

        return JsonResponse(data, safe=False)
        
    @api_view(['POST'])
    def exitChannel(request):
        token = request.data['token']
        channel_id = uuid.UUID(uuid.UUID(request.data['channel_id']).hex)
        data = OrderedDict()
        
        user_token = Token.objects.filter(key = token)
        channel = Channel.objects.filter(url_id = channel_id)
        
        if not(user_token.exists()):
            data["state"] = "fail"
            data["message"] = "Token is not exist"
        elif not(channel.exists()):
            data["state"] = "fail"
            data["message"] = "Channel is not exist"
        else:
            user = User.objects.get(id = user_token[0].user_id)
            if not(Guest.objects.filter(user = user, channel = channel[0]).exists()):
                data["state"] = "fail"
                data["message"] = "User is not channel\'s guest"
            elif (Host.objects.filter(user = user, channel = channel[0]).exists()):
                data["state"] = "fail"
                data["message"] = "Host cannot exit channel"

        if bool(data):
            json.dumps(data, ensure_ascii=False, indent="\t")
            return JsonResponse(data, safe=False)

        user = User.objects.get(id = user_token[0].user_id)
        guest = Guest.objects.get(user = user, channel = channel[0])
        guest.delete()

        units = Unit.objects.filter(channel = channel[0])
        unittests = UnitTest.objects.filter(unit__in = units)
        tests = TestPlan.objects.filter(id__in = unittests.values_list('test', flat=True))
        testsets = TestSet.objects.filter(user = user, test__in = tests)
        testsets.delete()

        #feed 삭제 부분
        newses = News.objects.filter(channel = channel[0])
        UserNews.objects.filter(news__in = newses, user = user).delete()
        
        data["state"] = "success"
        data["message"] = "Exit the channel completed"

        host_channel_list = channelManager.requestHostChannelList(token)
        guest_channel_list = channelManager.requestGuestChannelList(token)
        host_length = len(host_channel_list)
        guest_length = len(guest_channel_list)

        data["leader"] = [0 for i in range(host_length)]
        for i in range(host_length):
            host_channel = Channel.objects.filter(id=host_channel_list[i].id)
            serializer = ChannelIDSerializer(host_channel, many=True)
            data["leader"][i] = OrderedDict()
            data["leader"][i]["id"] = serializer.data[0]['url_id']
            data["leader"][i]["title"] = host_channel_list[i].name
            data["leader"][i]["detail"] = host_channel_list[i].description
            data["leader"][i]["image"] = host_channel_list[i].image_type

        data["runner"] = [0 for i in range(guest_length)]
        for i in range(guest_length):
            guest_channel = Channel.objects.filter(id=guest_channel_list[i].id)
            serializer = ChannelIDSerializer(guest_channel, many=True)
            data["runner"][i] = OrderedDict()
            data["runner"][i]["id"] = serializer.data[0]['url_id']
            data["runner"][i]["title"] = guest_channel_list[i].name
            data["runner"][i]["detail"] = guest_channel_list[i].description
            data["runner"][i]["image"] = guest_channel_list[i].image_type

        json.dumps(data, ensure_ascii=False, indent="\t")

        return JsonResponse(data, safe=False)
