from django.conf.urls import url
from . import views, ajax_views


app_name = 'game'
urlpatterns = [
    url(r'^$', views.CreateGameView.as_view(), name='create'),
    url(r'^ranking/$', views.RankingView.as_view(), name='ranking'),
    url(r'^match/(?P<signed_id>.+)/$', views.GameView.as_view(), name='match'),
    url(r'^sweep/(?P<signed_id>.+)/$', ajax_views.sweep_view, name='sweep'),
    url(r'^flag/(?P<signed_id>.+)/$', ajax_views.flag_view, name='flag'),
]
