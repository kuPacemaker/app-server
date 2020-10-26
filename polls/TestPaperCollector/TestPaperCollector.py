from django.http import JsonResponse
from polls.models import *
from polls.serializers import *
from collections import OrderedDict
from rest_framework.decorators import api_view
import json
import random

class testPaperCollector():
    @api_view(['POST'])
    def requestPaper(request):
        token = request.data['token']
        unit_id = request.data['unit_id']
        data = orderedDict()

        user_token = Token.objects.filter(key = token)
        unit = Unit.objects.filter(url_id = unit_id)
        if not (user_token.exists()):
            data["message"] = 'Token is not exist'
        elif not (unit.exists()):
            data["message"] = 'Unit is not exist'
        elif not (TestPlan.objects.filter(unit = unit[0]).exists()):
            data["message"] = 'TestPlan is not exist'
        else:
            test = TestPlan.objects.get(unit = unit[0])
            user = User.objects.get(id = user_token[0].user_id)
            if not (TestSet.objects.filter(user = user, test = test).exists()):
                data["message"] = 'User does not have Test of Unit'

        if bool(data):
            json.dumps(data, ensure_ascii=False, indent="\t")
            return JsonResponse(data, safe=False)

        user = User.objects.get(id = Token.objects.get(key = token).user_id)
        unit = Unit.objects.get(url_id = unit_id)

        test = UnitTest.objects.get(unit = unit).test
        testset = TestSet.objects.get(user = user, test = test)

        qaset = UnitQA.objects.get(unit = unit).qaset
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
            TestPair.objects.create(tset = testset, qapair = qapair)

        testset.received = True
        testset.save()

        #data should be included
        '''
        each testpair:
            testpair.url_id
            testpair.qapair.question
            testpair.qapair.answer_set
        '''

        json.dumps(data, ensure_ascii=False, indent="\t")

        return JsonResponse(data, safe=False)

    @api_view(['POST'])
    def submitPaper(request): #pairs = [{"id", "user_answer"}] testpair's id, user_answer
        token = request.data['token']
        unit_id = request.data['unit_id']
        pairs = request.data['pairs']
        data = OrderedDict()

        user_token = Token.objects.filter(key = token)
        unit = Unit.objects.filter(url_id = unit_id)
        if not (user_token.exists()):
            data["message"] = 'Token is not exist'
        elif not (unit.exists()):
            data["message"] = 'Unit is not exist'
        elif not (TestPlan.objects.filter(unit = unit[0]).exists()):
            data["message"] = 'TestPlan is not exist'
        else:
            test = TestPlan.objects.get(unit = unit[0])
            user = User.objects.get(id = user_token[0].user_id)
            if not (TestSet.objects.filter(user = user, test = test).exists()):
                data["message"] = 'User does not have Test of Unit'

        if bool(data):
            json.dumps(data, ensure_ascii=False, indent="\t")
            return JsonResponse(data, safe=False)

        user = User.objects.get(id = Token.objects.get(key = token).user_id)
        testset = TestSet.objects.get(user = user, test = UnitTest.objects.get(unit = unit).test)
        testset.submitted = True
        testset.save()

        for pair in pairs:
            testpair = TestPair.objects.get(url_id = pair["id"])
            testpair.user_answer = pair["user_answer"]
            testpair.save()

        data["message"] = 'Paper submitted'

        json.dumps(data, ensure_ascii=False, indent="\t")

        return JsonResponse(data, safe=False)
