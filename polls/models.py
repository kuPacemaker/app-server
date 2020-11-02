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

class User(AbstractUser):
    url_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    username = models.CharField(unique=True, default='', max_length=128)
    first_name = modles.CharField(unique=True, default='', max_length=128)

    @receiver(post_save, sender = settings.AUTH_USER_MODEL)
    def create_auth_token(sender, instance=None, created=False, **kwargs):
        if created:
            Token.objects.create(user=instance)

class BKD(models.Model):
    url_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=72)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Channel(models.Model):
    url_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=100, blank=True)
    accesspath = models.CharField(max_length=20, unique=True, null=True)
    image_type = models.IntegerField(default = 0)
    
class Unit(models.Model):
    url_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    channel = models.ForeignKey(Channel, db_column='ch_id', on_delete=models.CASCADE)
    index = models.IntegerField(default=0)
    name = models.CharField(max_length=20)

    class Meta:
        unique_together = [['channel', 'index']]
    
    def save(self, *args, **kwargs):
        if not self.pk:
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
    answer = models.CharField(max_length=100)
    answer_set = models.CharField(max_length=500)
    
    class Meta:
        unique_together = [['qaset', 'index']]
    
    def save(self, *args, **kwargs):
        if not self.pk:
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
    user_answer = models.CharField(max_length=100, blank=True)
    correct = models.BooleanField(default=False)

    class Meta:
        unique_together =[['tset', 'pair']]

class News(models.Model):
    ntype = models.CharField(max_length=20, null=True)
    title = models.CharField(max_length=50, null=True)
    body = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    channel = models.ForeignKey(Channel, db_column='ch_id', on_delete=models.CASCADE, null=True)
    unit = models.ForeignKey(Unit, db_column='unit_id', on_delete=models.CASCADE, null=True)

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
    bkd = models.OneToOneField(BKD, db_column='bkd_id', on_delete=models.CASCADE)
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
