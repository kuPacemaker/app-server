from django.urls import path

from . import views
from .AccountManager.AccountManager import accountManager

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



#urlpatterns = []
urlpatterns += account_url_patterns
