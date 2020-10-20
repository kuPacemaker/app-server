# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

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
    url_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    username = models.CharField(unique=True, default='', max_length=30)

    @receiver(post_save, sender = settings.AUTH_USER_MODEL)
    def create_auth_token(sender, instance=None, created=False, **kwargs):
        if created:
            Token.objects.create(user=instance)

class BKD(models.Model):
    url_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=20)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Channel(models.Model):
    url_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=100, blank=True)
    accesspath = models.CharField(max_length=20, unique=True, null=True)
    
class Unit(models.Model):
    url_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    channel = models.ForeignKey(Channel, db_column='ch_id', on_delete=models.CASCADE)
    index = models.IntegerField(default=0)
    name = models.CharField(max_length=20)

    class Meta:
        unique_together = [['channel', 'index']]
    
    def save(self, *args, **kwargs):
        self.index = Unit.objects.filter(channel=self.channel).count()+1
        super(Unit, self).save(*args, **kwargs)

class QASet(models.Model):
    url_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    valid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class QAPair(models.Model):
    url_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    qaset = models.ForeignKey(QASet, db_column='set_id', on_delete=models.CASCADE)
    index = models.IntegerField(default=0)
    question = models.CharField(max_length=200)
    answer = models.CharField(max_length=20)
    answer_set = models.CharField(max_length=100)
    
    class Meta:
        unique_together = [['qaset', 'index']]
    
    def save(self, *args, **kwargs):
        self.index = QAPair.objects.filter(qaset=self.qaset).count()+1
        super(QAPair, self).save(*args, **kwargs)

class TestPlan(models.Model):
    url_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    qaset = models.ForeignKey(QASet, db_column='set_id', on_delete=models.CASCADE)
    que_number = models.IntegerField(null=True)
    release_time = models.DateTimeField(null=True)
    released = models.BooleanField(default=False)
    end_time = models.DateTimeField(null=True)
    ended = models.BooleanField(default=False)

class TestSet(models.Model):
    url_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, db_column='user_id', on_delete=models.CASCADE)
    test = models.ForeignKey(TestPlan, db_column='test_id', on_delete=models.CASCADE)
    received = models.BooleanField(default=False)
    submitted = models.BooleanField(default=False)
    score = models.FloatField(default=0.0)

    class Meta:
        unique_together = [['user', 'test']]

class TestPair(models.Model):
    url_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    tset = models.ForeignKey(TestSet, db_column='tset_id', on_delete=models.CASCADE)
    pair = models.ForeignKey(QAPair, db_column='pair_id', on_delete=models.CASCADE)
    user_answer = models.CharField(max_length=20, blank=True)
    correct = models.BooleanField(default=False)

    class Meta:
        unique_together =[['tset', 'pair']]

class News(models.Model):
    body = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

#Relationship
class Host(models.Model):
    user = models.ForeignKey(User, db_column='user_id', on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, db_column='ch_id', on_delete=models.CASCADE)

class Guest(models.Model):
    user = models.ForeignKey(User, db_column='user_id', on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, db_column='ch_id', on_delete=models.CASCADE)

class BKDOwner(models.Model):
    user = models.ForeignKey(User, db_column='user_id', on_delete=models.CASCADE)
    bkd = models.OneToOneField(BKD, db_column='bkd_id', on_delete=models.CASCADE)

class UnitBKD(models.Model):
    bkd = models.ForeignKey(BKD, db_column='bkd_id', on_delete=models.CASCADE)
    unit = models.OneToOneField(Unit, db_column='unit_id', on_delete=models.CASCADE)
    opened = models.BooleanField(default=False)

class UnitQA(models.Model):
    qaset = models.OneToOneField(QASet, db_column='set_id', on_delete=models.CASCADE)
    unit = models.OneToOneField(Unit, db_column='unit_id', on_delete=models.CASCADE)

class UnitTest(models.Model):
    test = models.OneToOneField(TestPlan, db_column='test_id', on_delete=models.CASCADE)
    unit = models.OneToOneField(Unit, db_column='unit_id', on_delete=models.CASCADE)

class UserNews(models.Model):
    user = models.ForeignKey(User, db_column='user_id', on_delete=models.CASCADE)
    news = models.ForeignKey(News, db_column='news_id', on_delete=models.CASCADE)

'''
class BKDToQA(models.Model):
    bkd = models.ForeignKey(BKD, db_column='bkd_id', on_delete=models.CASCADE)
    qaset = models.OneToOneField(QASet, db_column='set_id', on_delete=models.CASCADE)
'''

'''
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
