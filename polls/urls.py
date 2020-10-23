from django.urls import path

from . import views
from .AccountManager.AccountManager import accountManager
from .FileManager.BKDManager.BKDManager import bkdManager
from .ChannelManager.ChannelManager import channelManager
from .ChannelManager.GuestChannel.GuestChannel import guestChannel
from .ChannelManager.HostChannel.HostChannel import hostChannel
from .QGAPI.QGAPI import qgapi

app_name = 'polls'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('<int:question_id>/vote/', views.vote, name='vote'),
]

account_url_patterns = [
    path('signIn/<str:uid>/<str:pw>/',accountManager.signIn, name='signIn'),
    path('signUp/<str:uid>/<str:name>/<str:pw>/',accountManager.signUp, name='signUp'),
    path('findAccount/<str:uid>/',accountManager.findAccount, name='findAccount'),
    path('modifyAccount/<str:token>/<str:uid>/<str:name>/<str:pw>/<str:pw_new>/',accountManager.modifyAccount, name='modifyAccount'),
]

bkd_url_patterns = [
    path('requestBKD/<str:token>/<uuid:unit>/',bkdManager.requestBKD, name='requestBKD'),
    path('createBKD/<str:token>/<uuid:unit>/',bkdManager.createBKD, name='createBKD'),
    path('editBKD/<str:token>/<uuid:bkd_id>/<str:visible>/<str:title>/<str:body>/',bkdManager.editBKD, name='editBKD'),
    path('deleteBKD/<str:token>/<uuid:bkd_id>/',bkdManager.deleteBKD, name='deleteBKD'),
]

qg_url_patterns = [
    path('generateQuestion/<int:document>/',qgapi.generateQuestion, name='questionGenerate'),
]

channel_url_patterns = [
    path('createChannel/<str:token>/',channelManager.createChannel, name='createChannel'),
    path('deleteChannel/<str:token>/<uuid:channel_id>/',channelManager.deleteChannel, name='deleteChannel'),
    path('editChannel/<str:token>/<uuid:channel_id>/<str:channel_name>/<str:channel_desc>/',channelManager.editChannel, name='editChannel'),
    path('enterChannel/<str:token>/<str:accesscode>/',guestChannel.enterChannel, name='enterChannel'),
]

unit_url_patterns = [
    path('createUnit/<str:token>/<uuid:channel>/<int:index>/<str:title>/',hostChannel.createUnit, name='createUnit'),
    path('deleteUnit/<str:token>/<uuid:unit_id>/',hostChannel.deleteUnit, name='deleteUnit'),
]

#urlpatterns = []
urlpatterns += account_url_patterns
urlpatterns += bkd_url_patterns
urlpatterns += qg_url_patterns
urlpatterns += channel_url_patterns
urlpatterns += unit_url_patterns
