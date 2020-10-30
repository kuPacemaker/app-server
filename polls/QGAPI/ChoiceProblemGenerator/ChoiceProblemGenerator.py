from polls.models import *
import random

class choiceProblemGenerator():
    def choiceProblemGenerator(nouns, aqset):
        count = len(nouns)
        length = len(aqset)
        count_for_arr = 0

        question = [0 for i in range(length)]
        answer = [0 for i in range(length)]
        answerset = ["" for i in range(length)]

        for i in range(length):
            #이미 answerset에 추가된 단어를 담아두는 배열 prev_random_nouns
            prev_random_nouns = []
            #랜덤한 정답의 위치를 지정해주는 random_answer_position
            random_answer_position = random.randint(0,3)
            question[i] = aqset[i][1]
            answer[i] = aqset[i][0]
            for j in range(4):
                #j가 정답의 위치에 해당하는 index값과 다르다면
                if(j != random_answer_position):
                    #객관식의 보기로 넣기 위한 명사를 랜덤하게 뽑기위한 index가 될 random_noun_choice
                    random_noun_choice = random.randint(0,count-1)
                    #answerset에 추가된 단어가 없다면
                    if(len(prev_random_nouns) == 0):
                        #정답이랑 일치하지 않는 명사를 뽑을때까지 랜덤함수 반복
                        while(answer[i] == nouns[random_noun_choice]):
                            random_noun_choice = random.randint(0,count-1)
                    #answerset에 추가된 단어가 있다면
                    else:
                        #정답이랑도 일치하지 않고, answerset에 추가되지도 않은 명사를 뽑을때까지 랜덤함수 반복
                        while((answer[i] == nouns[random_noun_choice]) or (prev_random_nouns[0] == nouns[random_noun_choice]) or (prev_random_nouns[-1] == nouns[random_noun_choice)):
                            random_noun_choice = random.randint(0,count-1)
                    #answerset에 추가된 단어를 담아두는 배열에다가 answerset에 추가된 단어를 넣음
                    prev_random_nouns.append(nouns[random_noun_choice])
                    #answerset에 해당 단어를 추가
                    answerset[i] += nouns[random_noun_choice]
                #j가 정답의 위치에 해당하는 index값과 같다면
                else:
                    #answerset에 정답을 추가
                    answerset[i] += answer[i]
                #뒤에 올 단어가 존재한다면
                if(j != 3):
                    #각 quiz의 보기들을 |^|로 구별하여 하나의 문자열로 만들어준다.
                    answerset[i] += "|^|"
        
        qa_set = QASet.objects.create(valid = False)
        for i in range(length):
            QAPair.objects.create(qaset = qa_set, index = i+1, question = question[i], answer = answer[i], answer_set = answerset[i])

        return qa_set
