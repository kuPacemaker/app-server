from polls.models import *
import random

class choiceProblemGenerator():
    def choiceProblemGenerator(nouns, aqset):
        print(nouns)
        print(aqset)
        count = len(nouns)
        length = len(aqset)
        print(length)

        question = [0 for i in range(length)]
        answer = [0 for i in range(length)]
        answerset = [[0 for col in range(4)]for row in range(length)]

        for i in range(length):
            random_answer_position = random.randint(0,3)
            question[i] = aqset[i][1]
            answer[i] = aqset[i][0]
            for j in range(4):
                if(j != random_answer_position):
                    random_noun_choice = random.randint(0,count-1)
                    while(random_noun_choice == i):
                        random_noun_choice = random.randint(0,count)
                    answerset[i][j] = nouns[random_noun_choice] 
                else:
                    answerset[i][j] = answer[i]
        
        qa_set = QASet.objects.create(valid = False)
        for i in range(length):
            qa_pair = QAPair.objects.create(qaset = qa_set, index = i+1, question = question[i], answer = answer[i], answer_set = answerset[i])

