from .ChannelJoinCodeGenerator.ChannelJoinCodeGenerator import channelJoinCodeGenerator
from django.http import JsonResponse
from polls.models import *

class hostChannel():
    def ChannelJoinCodeGenerate():
        joinCode = channelJoinCodeGenerator.channelJoinCodeGenerate() #생성된 채널코드

        return joinCode

    def excludeChannelMember():

    def createUnit(request, token, channel, index, title):
        user_token = Token.objects.filter(token = token)
        if(user_token):
            #token 존재
            print("TOKEN IS ExIST")
            user_token = Token.objects.get(token = token)
            user = User.objects.get(id = user_token.user_id)
            host = Host.objects.filter(user=user)

        else:
            #token 미존재
            print("TOKEN IS NOT EXIST")

    def editUnit(request, token, cid, cname, cdesc):

    def deleteUnit(request, token, cid):

    def registerBKD():

    def requestChapterList():

    def enterHostChannel():

    def browseHostChapter():

