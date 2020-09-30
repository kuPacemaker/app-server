from django.urls import path

from . import views
from .AccountManager.AccountManager import accountManager
from .FileManager.BKDManager.BKDManager import bkdManager
from .QGAPI.QGAPI import qgapi

app_name = 'polls'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('<int:question_id>/vote/', views.vote, name='vote'),
]

account_url_patterns = [
    path('login/<str:uid>/<str:upw>/',accountManager.login, name='login'),
    path('signIn/<str:uid>/<str:upw>/<str:uname>/',accountManager.signIn, name='signIn'),
    path('findAccount/<str:uid>/',accountManager.findAccount, name='findAccount'),
    path('modifyAccountInfo/<str:uid>/<str:uname>/<str:upw>/<str:newpw>/',accountManager.modifyAccountInfo, name='modifyAccountInfo'),
]

bkd_url_patterns = [
    path('inquireIntoBKD/<str:title>/',bkdManager.inquireIntoBKD, name='inquireIntoBKD'),
    path('makeBKD/',bkdManager.makeBKD, name='makeBKD'),
    path('saveBKD/<int:bkd_id>/<str:title>/<str:body>/',bkdManager.saveBKD, name='saveBKD'),
    path('deleteBKD/<str:title>/',bkdManager.deleteBKD, name='deleteBKD'),
]

qg_url_patterns = [
    path('makeProblem/<int:bkd_id>/',qgapi.questionGenerate, name='makeProblem'),
]

#urlpatterns = []
urlpatterns += account_url_patterns
urlpatterns += bkd_url_patterns
urlpatterns += qg_url_patterns
