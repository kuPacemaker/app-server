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
                host = Host.objects.filter(user=user)
                if(host):
                    #호스트가 자기자신의 채널로 입장을 시도하면 입장불가
                    data["state"] = "fail"
                    data["message"] = "Host cannot enter their own channel"
                else:
                    host_channel_list = channelManager.requestHostChannelList(token)
                    guest_channel_list = channelManager.requestGuestChannelList(token)
                    host_length = len(host_channel_list)
                    guest_length = len(guest_channel_list)
        
                    data["state"] = "success"
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

                    data["runner"] = [0 for i in range(guest_length+1)]
                    for i in range(guest_length):
                        guest_channel = Channel.objects.filter(id=guest_channel_list[i].id)
                        serializer = ChannelIDSerializer(guest_channel,many=True)
                        #UUID가 serializable하도록 해주기 위해 url_id만 별도의 serializer를 돌림
                        data["runner"][i] = OrderedDict()
                        data["runner"][i]["id"] = serializer.data[0]['url_id']
                        data["runner"][i]["title"] = guest_channel_list[i].name
                        data["runner"][i]["detail"] = guest_channel_list[i].description
                        data["runner"][i]["image"] = guest_channel_list[i].image_type
		        
                    #이 아래부분은 새로 입장하는 채널을 추가하는 부분인데
                    #이미 입장해있는 채널인지 여부를 확인해주는 부분이
                    #추가되어야 한다
                    serializer = ChannelInfoSerializer(channel, many=True)
                    data["runner"][guest_length] = OrderedDict()
                    data["runner"][guest_length]["id"] = serializer.data[0]['url_id']
                    data["runner"][guest_length]["title"] = serializer.data[0]['name']
                    data["runner"][guest_length]["detail"] = serializer.data[0]['description']
                    data["runner"][guest_length]["image"] = serializer.data[0]['image_type']

                    channel = Channel.objects.get(accesspath = accesscode)
                    Guest.objects.create(user=user,channel=channel)
            
        else:
            data["state"] = "fail"
            data["message"] = "Token is not exist"

        json.dumps(data, ensure_ascii=False, indent="\t")

        return JsonResponse(data, safe=False)
        

#def browseGuestChapter():

#def withdrawChannel():

#def joinChannel():

