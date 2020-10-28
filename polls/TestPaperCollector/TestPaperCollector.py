from django.http import JsonResponse
from polls.models import *
from polls.serializers import *
from polls.QGAPI.QGAPI import qgapi
from collections import OrderedDict
from rest_framework.decorators import api_view
import json, uuid
import random

class testPaperCollector():
    @api_view(['POST'])
    def requestPaper(request):
        token = request.data['token']
        unit_id = request.data['unit_id']
        data = OrderedDict()

        user_token = Token.objects.filter(key = token)
        unit = Unit.objects.filter(url_id = unit_id)
        if not (user_token.exists()):
            data["state"] = "fail"
            data["message"] = "Token is not exist"
        elif not (unit.exists()):
            data["state"] = "fail"
            data["message"] = "Unit is not exist"
        elif not (UnitTest.objects.filter(unit = unit[0]).exists()):
            data["state"] = "fail"
            data["message"] = "TestPlan is not exist"
        else:
            test = UnitTest.objects.get(unit = unit[0]).test
            user = User.objects.get(id = user_token[0].user_id)
            if not (TestSet.objects.filter(user = user, test = test).exists()):
                data["state"] = "fail"
                data["message"] = "User does not have Test of Unit"

        if bool(data):
            json.dumps(data, ensure_ascii=False, indent="\t")
            return JsonResponse(data, safe=False)

        user = User.objects.get(id = user_token[0].user_id)

        test = UnitTest.objects.get(unit = unit[0]).test
        testset = TestSet.objects.get(user = user, test = test)

        qaset = UnitQA.objects.get(unit = unit[0]).qaset
        qapairs = QAPair.objects.filter(qaset = qaset)
        pair_length = qapairs.count()

        pair_list = []
        ran_num = random.randint(1, pair_length)
        for i in range(test.que_number):
            while ran_num in pair_list:
                ran_num = random.randint(1, pair_length)
            pair_list.append(ran_num)

        for index in pair_list:
            qapair = QAPair.objects.get(qaset = qaset, index = index)
            TestPair.objects.create(tset = testset, pair = qapair)

        testset.received = True
        testset.save()

        #data should be included
        '''
        each testpair:
            testpair.url_id
            testpair.qapair.question
            testpair.qapair.answer_set
        '''
        data["state"] = "success"
        data["questions"] = [0 for i in range(test.que_number)]
        testpair = TestPair.objects.filter(tset = testset)
        serializer = TestPairIDSerializer(testpair, many=True)
        for i in range(test.que_number):
            data["questions"][i] = OrderedDict()
            data["questions"][i]["id"] = serializer.data[i]['url_id']
            data["questions"][i]["index"] = i+1
            data["questions"][i]["quiz"] = testpair[i].pair.question
            data["questions"][i]["answer_set"] = qgapi.stringWithSlash(testpair[i].pair.answer_set)

        json.dumps(data, ensure_ascii=False, indent="\t")

        return JsonResponse(data, safe=False)

    @api_view(['POST'])
    def submitPaper(request): #pairs = [{"id", "user_answer"}] testpair's id, user_answer
        token = request.data['token']
        unit_id = request.data['unit_id']
        pairs = request.data['pairs']
        pairs_length = len(pairs)
        pair_id_list = [0 for i in range(pairs_length)]
        pair_answer_list = [0 for i in range(pairs_length)]
        for i in range(pairs_length):
            pair_id_list[i] = uuid.UUID(uuid.UUID(pairs[i]['id']).hex)
            pair_answer_list[i] = pairs[i]['user_answer']
        data = OrderedDict()

        user_token = Token.objects.filter(key = token)
        unit = Unit.objects.filter(url_id = unit_id)
        if not (user_token.exists()):
            data["state"] = "fail"
            data["message"] = "Token is not exist"
        elif not (unit.exists()):
            data["state"] = "fail"
            data["message"] = "Unit is not exist"
        elif not (UnitTest.objects.filter(unit = unit[0]).exists()):
            data["state"] = "fail"
            data["message"] = "TestPlan is not exist"
        else:
            test = UnitTest.objects.get(unit = unit[0]).test
            user = User.objects.get(id = user_token[0].user_id)
            if not (TestSet.objects.filter(user = user, test = test).exists()):
                data["state"] = "fail"
                data["message"] = "User does not have Test of Unit"

        if bool(data):
            json.dumps(data, ensure_ascii=False, indent="\t")
            return JsonResponse(data, safe=False)

        user = User.objects.get(id = Token.objects.get(key = token).user_id)
        test = UnitTest.objects.get(unit = unit[0]).test
        testset = TestSet.objects.get(user = user, test = test)
        testset.submitted = True
        testset.save()

        for i in range(pairs_length):
            qapair = QAPair.objects.get(url_id = pair_id_list[i])
            testpair = TestPair.objects.get(pair = qapair,tset = testset)
            testpair.user_answer = pair_answer_list[i]
            testpair.save()

        testset = TestSet.objects.filter(test = test)
        for i in range(testset.count()):
            if(testset[i].submitted == False):
                break
            if(i == testset.count()-1):
                test.ended = True
                test.save()
                    
                unit_for_news = Unit.objects.get(url_id = unit_id)
                channel_for_news = unit_for_news.channel
                news_title = "Submit all papers"
                news_body = channel_for_news.name+"\'s all runners are finish submitted paper."
                news = News.objects.create(title = news_title, body = news_body, channel = channel_for_news, unit = unit_for_news)
                hosts = Host.objects.filter(channel = channel_for_news)
                for host in hosts:
                    UserNews.objects.create(news = news, user = host.user)


        data["state"] = "success"
        data["message"] = "Paper submitted"

        json.dumps(data, ensure_ascii=False, indent="\t")

        return JsonResponse(data, safe=False)
