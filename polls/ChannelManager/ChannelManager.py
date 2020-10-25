from django.http import JsonResponse
from polls.models import *
from rest_framework.authtoken.models import Token
from polls.serializers import *
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

            data["leader"] = [0 for i in range(host_length+1)]
            for i in range(host_length):
                #기존의 host channel list
                host_channel = Channel.objects.filter(id=host_channel_list[i].id)
                serializer = ChannelIDSerializer(host_channel, many=True)
                data["leader"][i] = OrderedDict()
                data["leader"][i]["id"] = serializer.data[0]['url_id']
                data["leader"][i]["title"] = host_channel_list[i].name
                data["leader"][i]["detail"] = host_channel_list[i].description
                data["leader"][i]["image"] = None
               
            new_channel = Channel.objects.create(name=channel_name, description=channel_desc, accesspath=channel_join_code)
            Host.objects.create(channel = new_channel, user = user)
            channel = Channel.objects.filter(id=new_channel.id)
            serializer = ChannelInfoSerializer(channel,many=True)
            #새로 생성한 host channel list
            data["leader"][host_length] = OrderedDict()
            data["leader"][host_length]["id"] = serializer.data[0]['url_id']
            data["leader"][host_length]["title"] = serializer.data[0]['name']
            data["leader"][host_length]["detail"] = serializer.data[0]['description']
            data["leader"][host_length]["image"] = None

            if(guest_length != 0):
                data["runner"] = [0 for i in range(guest_length)]
                for i in range(guest_length):
                    guest_channel = Channel.objects.filter(id=guest_channel_list[i].id)
                    serializer = ChannelIDSerializer(guest_channel,many=True)
                    #UUID가 serializerable하도록 해주기 위해 url_id만 별도의 serailizer 사용
                    data["runner"][i] = OrderedDict()
                    data["runner"][i]["id"] = serializer.data[0]['url_id']
                    data["runner"][i]["title"] = guest_channel_list[i].name
                    data["runner"][i]["detail"] = guest_channel_list[i].description
                    data["runner"][i]["image"] = None
            else:
                data["runner"] = []
            
            json.dumps(data, ensure_ascii=False, indent="\t")

            return JsonResponse(data, safe=False)
        
        else:
            #token 미존재
            print("TOKEN IS NOT EXIST")

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
                    channel.name = channel_name
                    channel.description = channel_desc
                    channel.save()

                    channel = Channel.objects.filter(url_id = channel_id)
                    serializer = ChannelInfoSerializer(channel, many=True)

                    return JsonResponse(serializer.data[0], safe=False)
                
                else:
                    #해당 채널이 user의 것이 아님
                    data["message"] = 'User is not channel\'s host'

            else:
                #channel 미존재
                data["message"] = 'Channel is not exist'
            
        else:
            #token 미존재
            data["message"] = 'Token is not exist'
        
        json.dumps(data, ensure_ascii=False, indent = "\t")

        return JsonResponse(data, safe=False)


    @api_view(['POST'])
    def deleteChannel(request):
        token = request.data['token']
        channel_id = uuid.UUID(uuid.UUID(request.data['channel_id']).hex)
        user_token = Token.objects.filter(key = token)
        if(user_token):
            #token 존재
            channel = Channel.objects.filter(url_id = channel_id)
            if(channel):
                #channel 존재
                channel = Channel.objects.get(url_id = channel_id)
                host = Host.objects.get(channel = channel)
                host.delete()
                channel.delete()
            else:
                #channel 미존재
                print("CHANNEL IS NOT EXIST")
            
        else:
            #token 미존재
            print("TOKEN IS NOT EXIST")



#def excludeChannelMember():

