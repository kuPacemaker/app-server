from django.urls import path

from . import views
from .AccountManager.AccountManager import accountManager
from .FileManager.BKDManager.BKDManager import bkdManager
from .FeedManager.FeedManager import feedManager
from .ChannelManager.ChannelManager import channelManager
from .ChannelManager.GuestChannel.GuestChannel import guestChannel
from .ChannelManager.HostChannel.HostChannel import hostChannel
from .ChannelManager.HostChannel.ConsiderQuestion.ConsiderQuestion import considerQuestion
from .TestPaperCollector.TestPaperCollector import testPaperCollector
from .QGAPI.QGAPI import qgapi

app_name = 'polls'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
]

account_url_patterns = [
    path('signIn/',accountManager.signIn, name='signIn'),
    path('signUp/',accountManager.signUp, name='signUp'),
    path('findAccount/',accountManager.findAccount, name='findAccount'),
    path('modifyAccount/',accountManager.modifyAccount, name='modifyAccount'),
]

bkd_url_patterns = [
    path('requestBKD/',bkdManager.requestBKD, name='requestBKD'),
    path('createBKD/',bkdManager.createBKD, name='createBKD'),
    path('editBKD/',bkdManager.editBKD, name='editBKD'),
    path('deleteBKD/',bkdManager.deleteBKD, name='deleteBKD'),
]

qg_url_patterns = [
    path('generateQuestion/',qgapi.generateQuestion, name='questionGenerate'),
    path('verifyQuestion/',considerQuestion.verifyQuestion, name='verifyQuestion'),
    path('makeReservation/',considerQuestion.makeReservation, name='makeReservation'),
]

paper_url_patterns = [
    path('requestPaper/',testPaperCollector.requestPaper, name='requestPaper'),
    path('submitPaper/',testPaperCollector.submitPaper, name='submitPaper'),
]

channel_url_patterns = [
    path('createChannel/',channelManager.createChannel, name='createChannel'),
    path('deleteChannel/',channelManager.deleteChannel, name='deleteChannel'),
    path('editChannel/',channelManager.editChannel, name='editChannel'),
    path('enterChannel/',guestChannel.enterChannel, name='enterChannel'),
    path('requestChannel/',channelManager.requestChannel, name='requestChannel'),
]

unit_url_patterns = [
    path('createUnit/',hostChannel.createUnit, name='createUnit'),
    path('deleteUnit/',hostChannel.deleteUnit, name='deleteUnit'),
    path('requestUnit/',channelManager.requestUnit, name='requestUnit'),
]

feed_board_url_patterns = [
    path('requestBoard/',channelManager.requestBoard, name='requestBoard'),
    path('refresh/',feedManager.refresh, name='refresh'),
]

#urlpatterns = []
urlpatterns += account_url_patterns
urlpatterns += bkd_url_patterns
urlpatterns += qg_url_patterns
urlpatterns += paper_url_patterns
urlpatterns += channel_url_patterns
urlpatterns += unit_url_patterns
urlpatterns += feed_board_url_patterns
