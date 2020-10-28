from django.http import JsonResponse
from polls.models import *
from polls.serializers import *
from rest_framework.authtoken.models import Token
from collections import OrderedDict
from rest_framework.decorators import api_view
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
        serizliaer = NewsSerializer(news, many=True)
        data["board"] = OrderedDict()
        data["board"]["newsfeed"] = [0 for i in range(news_length)]
        for i in range(news_length):
            data["board"]["newsfeed"][i] = OrderedDict()
            data["board"]["newsfeed"][i]["type"] = serializer.data[i]['ntype']
            data["board"]["newsfeed"][i]["title"] = serializer.data[i]['title']
            data["board"]["newsfeed"][i]["body"] = serializer.data[i]['body']
            news_channel = Channel.objects.filter(id = news[i].channel.id)
            cid_serializer = ChannelIDSerializer(news_channel, many=True)
            data["board"]["newsfeed"][i]["arg"]["channel_id"] = cid_serializer.data[0]['url_id']
            news_unit = Unit.objects.filter(id = news[i].unit.id)
            uid_serializer = UnitIDSerializer(news_unit, many=True)
            data["board"]["newsfeed"][i]["arg"]["unit_id"] = uid_serializer.data[0]['url_id']

        hosts = Host.objects.filter(user = user)
        host_channel = Channel.objects.filter(id__in = hosts.values_list('channel', flat=True))
        host_length = host_channel.count()
        serializer = ChannelInfoSerializer(host_channel, many=True)
        data["board"]["leader"] = [0 for i in range(host_length)]
        for i in range(host_length):
            data["board"]["leader"][i] = OrderedDict()
            data["board"]["leader"][i]["id"] = serializer.data[i]['url_id']
            data["board"]["leader"][i]["title"] = serializer.data[i]['name']
            data["board"]["leader"][i]["detail"] = serializer.data[i]['description']
            data["board"]["leader"][i]["image"] = None

        guests = Guest.objects.filter(user = user)
        guest_channel = Channel.objects.filter(id__in = guests.values_list('channel', flat=True))
        guest_length = guest_channel.count()
        serializer = ChannelInfoSerializer(guest_channel, many=True)
        data["board"]["runner"] = [0 for i in range(guest_length)]
        for i in range(guest_length):
            data["board"]["runner"][i] = OrderedDict()
            data["board"]["runner"][i]["id"] = serializer.data[i]['url_id']
            data["board"]["runner"][i]["title"] = serializer.data[i]['name']
            data["board"]["runner"][i]["detail"] = serializer.data[i]['description']
            data["board"]["runner"][i]["image"] = None

        json.dumps(data, ensure_ascii=False, indent="\t")

        return JsonResponse(data, safe=False)
