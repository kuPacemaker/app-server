from django.shortcuts import render
from polls.models import BKD, Question
from rest_framework.parsers import JSONParser
import requests
import json

class qgapi():
    def questionGenerate(request, bkd_id):
        bkd = BKD.objects.get(id = bkd_id)
        
        URL = 'http://117.16.136.170/restful/qg'
        data = {'bkd' : bkd.body}
        res = requests.post(URL, data=data)
        content = res.text
        print(res)
        print(content)
        print(json.loads(content))

        latest_question_list = Question.objects.order_by('-pub_date')[:5]
        context = {'latest_question_list':latest_question_list}
        return render(request, 'polls/index.html',context)

