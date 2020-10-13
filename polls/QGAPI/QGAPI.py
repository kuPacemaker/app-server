from django.shortcuts import render
from polls.models import BKD, Question
from rest_framework.parsers import JSONParser
from .ChoiceProblemGenerator.ChoiceProblemGenerator import choiceProblemGenerator
import requests
import json

class qgapi():
    def questionGenerate(request, bkd_id):
        bkd = BKD.objects.get(id = bkd_id)
        
        URL = 'http://117.16.136.170/restful/qg'
        data = {'bkd' : bkd.body}
        res = requests.post(URL, data=data)
        content = res.text
        nouns = []
        aqset = []
        question_data = json.loads(content)
        length = len(question_data['passages'])
        for i in range(length):
            nouns += question_data['passages'][i]['nouns']
            aqset += question_data['passages'][i]['aqset']
    
        choiceProblemGenerator.choiceProblemGenerator(nouns,aqset)

        latest_question_list = Question.objects.order_by('-pub_date')[:5]
        context = {'latest_question_list':latest_question_list}
        return render(request, 'polls/index.html',context)

