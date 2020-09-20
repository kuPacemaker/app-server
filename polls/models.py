# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

import datetime, uuid

# Create your models here.


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now
    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text

class User(AbstractUser):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(unique=True, default='', max_length=30)

'''
class User(models.Model):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.CharField(max_length=30)
    password = models.CharField(max_length=30)
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name



class User(models.Model):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.CharField(max_length=20, editable=False)
    password = models.CharField(max_length=20)
    name = models.CharField(max_length=20)

class BKDGroup(models.Model):
    owner_id = models.ForeignKey('user_id.User', on_delete=models.CASCADE)
    bkdg_id = models.AutoField(editable=False)
    name = models.CharField(max_length=20)
    
    class Meta:
        unique_together = [['owner_id', 'bkdg_id']] #temporary key
    
class BKD(models.Model):
    bkd_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner_id = models.ForeignKey('user_id.User', on_delete=models.CASCADE)
    bkdg_id = models.ForeignKey(BKDGroup, on_delete=models.SET_NULL)
    title = models.CharField(max_length=20)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Channel(models.Model):
    ch_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=20)
    accesspath = models.UUIDField()
    description = models.CharField(max_length=20)
    
class Chapter(models.Model):
    ch_id = models.ForeignKey(Channel, on_delete=models.CASCADE)
    chap_id = models.AutoField()
    name = models.CharField(max_length=20)
    bkd_id = models.ForeignKey(BKD, on_delete=models.SET_NULL)
    opened = models.BooleanField(default=False)
    
    class Meta:
        unique_together = [['ch_id', 'chap_id']]
    
class Host(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    ch_id = models.ForeignKey(Channel, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = [['user_id', 'ch_id']]
    
class Guest(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    ch_id = models.ForeignKey(Channel, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = [['user_id', 'ch_id']]
    
class QASet(models.Model):
    set_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ch_id = models.ForeignKey(Channel, on_delete=models.CASCADE)
    chap_id = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    bkd_id = models.ForeignKey(BKD, on_delete=models.CASCADE)
    valid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
class QAPair(models.Model):
    set_id = models.ForeignKey(QASet, on_delete=models.CASCADE)
    pair_id = models.AutoField()
    question = models.CharField(max_length=50)
    answer = models.CharField(max_length=20)
    answer_set = models.CharField(max_length=100)
    
    class Meta:
        unique_together = [['set_id', 'pair_id']]
    
class Reservation(models.Model):
    set_id = models.ForeignKey(QASet, on_delete=models.CASCADE, primary_key=True)
    que_number = models.IntegerField()
    release_time = models.DateTimeField()
    end_time = models.DateTimeField()
    released = models.BooleanField(default=False)
    ended = models.BooleanField(default=False)
    
class QALock(models.Model):
    set_id = models.ForeignKey(QASet, on_delete=models.CASCADE, primary_key=True)
    ch_id = models.ForeignKey(Channel, on_delete=models.CASCADE)
    chap_id = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    bkd_id = models.ForeignKey(BKD, on_delete=models.CASCADE)
    
class Answer(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    set_id = models.ForeignKey(QAPair, on_delete=models.CASCADE)
    pair_id = models.ForeignKey(QAPair, on_delete=models.CASCADE)
    user_answer = models.CharField(max_length=20)
    answered = models.BooleanField(default=False)
    correct = models.BooleanField(default=False)
    
    class Meta:
        unique_together = [['user_id', 'set_id', 'pair_id']]
    
class News(models.Model):
    class NType(models.IntegerChoices):
        SYSTEM = 0
        USER = 1
        CHANNEL = 2
    
    news_id = models.AutoField(primary_key=True)
    news_type = models.IntegerField(choices=NType.chocies)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    ch_id = models.ForeignKey(Channel, on_delete=models.CASCADE)
    body = models.CharField(max_length=50)
    news_time = models.DateTimeField(auto_now_add=True)

class ClosedNews(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    news_id = models.ForeignKey(Channel, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = [['user_id', 'news_id']]
'''
