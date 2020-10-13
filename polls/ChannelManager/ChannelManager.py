from django.http import JsonResponse
from polls.models import *
from rest_framework.authtoken.models import Token
from polls.serializers import ChannelIDSerializer,ChannelInfoSerializer
from .HostChannel.ChannelJoinCodeGenerator.ChannelJoinCodeGenerator import channelJoinCodeGenerator

class channelManager():
#def requestHostChannelList():

#def requestGuestChannelList():

    def createChannel(request, token):
        user_token = Token.objects.filter(token = token)
        if(user_token):
            #token 존재
            channle_join_code = channelJoinCodeGenerator.channelJoinCodeGenerate()
            new_channel = Channel.objects.create(name = '', description = '', accesspath = channle_join_code)
            user_token = Token.objects.get(token = token)
            user = User.objects.get(id = user_token.user_id)
            channel = Channel.objects.filter(id = new_channel.id)
            Host.objects.create(user = user, channel = new_channel)
            serializer = ChannelIDSerializer(channel, many=True)
            
            return JsonResponse(serializer.data[0], safe=False)
        else:
            #token 미존재
            print("TOKEN IS NOT EXIST")

    def editChannel(request, token, channel_id, channel_name, channel_desc):
        user_token = Token.objects.filter(token = token)
        if(user_token):
            #token 존재
            channel = Channel.objects.filter(url_id = channel_id)
            if(channel):
                #channel 존재
                channel = Channel.objects.get(url_id = channel_id)
                channel.name = channel_name
                channel.description = channel_desc
                channel.save()

                channel = Channel.objects.filter(url_id = channel_id)
                serializer = ChannelInfoSerializer(channel, many=True)

                return JsonResponse(serializer.data[0], safe=False)

            else:
                #channel 미존재
                print("CHANNEL IS NOT EXIST")
            
        else:
            #token 미존재
            print("TOKEN IS NOT EXIST")

    def deleteChannel(request, token, channel_id):
        user_token = Token.objects.filter(token = token)
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

