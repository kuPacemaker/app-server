from django.http import JsonResponse
from polls.models import *
from polls.serializers import *
from rest_framework.authtoken.models import Token
from collections import OrderedDict
from rest_framework.decorators import api_view
from polls.ChannelManager.ChannelManager import channelManager
import json, uuid

#refresh에 필요
from datetime import date
import datetime

class feedManager():
    @api_view(['POST'])
    def refresh(request):
        token = request.data['token']
        data = OrderedDict()

        user_token = Token.objects.filter(key = token)
        if not (user_token.exists()):
            data["state"] = "fail"
            data["message"] = "Token is not exist"

        if bool(data):
            json.dumps(data, ensure_ascii=False, indent="\t")
            return JsonResponse(data, safe=False)

        user = User.objects.get(id = user_token[0].user_id)

        data["state"] = "success"
        usernews = UserNews.objects.filter(user = user).values_list('news', flat=True)
        limit_date = date.today() - datetime.timedelta(days=30)
        news = News.objects.filter(id__in = usernews, created_at__gte = limit_date)
        news_length = news.count()
        serializer = NewsSerializer(news, many=True)
        data["board"] = OrderedDict()
        data["board"]["newsfeed"] = [0 for i in range(news_length)]
        for i in range(news_length):
            data["board"]["newsfeed"][i] = OrderedDict()
            data["board"]["newsfeed"][i]["type"] = serializer.data[i]['ntype']
            data["board"]["newsfeed"][i]["title"] = serializer.data[i]['title']
            data["board"]["newsfeed"][i]["body"] = serializer.data[i]['body']
            news_channel = Channel.objects.filter(id = news[i].channel.id)
            cid_serializer = ChannelIDSerializer(news_channel, many=True)
            data["board"]["newsfeed"][i]["arg"] = OrderedDict()
            data["board"]["newsfeed"][i]["arg"]["channel_id"] = cid_serializer.data[0]['url_id']
            news_unit = Unit.objects.filter(id = news[i].unit.id)
            uid_serializer = UnitIDSerializer(news_unit, many=True)
            data["board"]["newsfeed"][i]["arg"]["unit_id"] = uid_serializer.data[0]['url_id']

        host_channel_list = channelManager.requestHostChannelList(token)
        guest_channel_list = channelManager.requestGuestChannelList(token)
        host_length = len(host_channel_list)
        guest_length = len(guest_channel_list)

        data["board"]["leader"] = [0 for i in range(host_length)]
        for i in range(host_length):
            host_channel = Channel.objects.filter(id=host_channel_llst[i].id)
            serializer = ChannelIDSerializer(host_channel, many=True)
            data["board"]["leader"][i] = OrderedDict()
            data["board"]["leader"][i]["id"] = serializer.data[0]['url_id']
            data["board"]["leader"][i]["title"] = host_channel_list[i].name
            data["board"]["leader"][i]["detail"] = host_channel_list[i].description
            data["board"]["leader"][i]["image"] = host_channel_list[i].image_type

        data["board"]["runner"] = [0 for i in range(guest_length)]
        for i in range(guest_length):
            guest_channel = Channel.objects.filter(id=guest_channel_list[i].id)
            serializer = ChannelIDSerializer(guest_channel, many=True)
            data["board"]["runner"][i] = OrderedDict()
            data["board"]["runner"][i]["id"] = serializer.data[0]['url_id']
            data["board"]["runner"][i]["title"] = guest_channel_list[i].name
            data["board"]["runner"][i]["detail"] = guest_channel_list[i].description
            data["board"]["runner"][i]["image"] = guest_channel_list[i].image_type

        json.dumps(data, ensure_ascii=False, indent="\t")

        return JsonResponse(data, safe=False)
