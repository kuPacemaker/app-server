from django.http import JsonResponse
from polls.models import *
from polls.serializers import *
from collections import OrderedDict
from ..ChannelManager import channelManager
import json

class guestChannel():
    def enterChannel(request, token, accesscode):
        user_token = Token.objects.filter(token = token)
        channel = Channel.objects.filter(accesspath = accesscode)
        data = OrderedDict()
        if(user_token):
            user_token = Token.objects.get(token = token)
            host_channel_list = channelManager.requestHostChannelList(token)
            guest_channel_list = channelManager.requestGuestChannelList(token)
            host_length = len(host_channel_list)
            guest_length = len(guest_channel_list)

            if(host_length != 0):
                data["leader"] = [0 for i in range(host_length)]
                for i in range(host_length):
                    host_channel = Channel.objects.filter(id=host_channel_list[i].id)
                    serializer = ChannelIDSerializer(host_channel,many=True)
                    data["leader"][i] = OrderedDict()
                    data["leader"][i]["id"] = serializer.data[0]['url_id']
                    data["leader"][i]["title"] = host_channel_list[i].name
                    data["leader"][i]["detail"] = host_channel_list[i].description
                    data["leader"][i]["image"] = None
            else:
                 data["leader"] = []

            if(guest_length != 0):
                if(channel):
                    data["runner"] = [0 for i in range(guest_length+1)]
                else:
                    data["runner"] = [0 for i in range(guest_length)]
                for i in range(guest_length):
                    guest_channel = Channel.objects.filter(id=guest_channel_list[i].id)
                    serializer = ChannelIDSerializer(guest_channel,many=True)
                    #UUID가 serializable하도록 해주기 위해 url_id만 별도의 serializer를 돌림
                    data["runner"][i] = OrderedDict()
                    data["runner"][i]["id"] = serializer.data[0]['url_id']
                    data["runner"][i]["title"] = guest_channel_list[i].name
                    data["runner"][i]["detail"] = guest_channel_list[i].description
                    data["runner"][i]["image"] = None
            else:
                data["runner"] = [0]
                data["runner"][0] = OrderedDict()

            if(channel):
                serializer = ChannelInfoSerializer(channel, many=True)
                data["runner"][guest_length]["id"] = serializer.data[0]['url_id']
                data["runner"][guest_length]["title"] = serializer.data[0]['name']
                data["runner"][guest_length]["detail"] = serializer.data[0]['description']
                data["runner"][guest_length]["image"] = None
            
            json.dumps(data, ensure_ascii=False, indent="\t")

            return JsonResponse(data, safe=False)
            
        else:
            print("TOKEN IS NOT EXIST")
        

#def browseGuestChapter():

#def withdrawChannel():

#def joinChannel():

