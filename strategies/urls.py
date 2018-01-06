from django.conf.urls import url, include
from . import views
urlpatterns = [
   url(r'^$', views.index, name='index'),
   url(r'^nifty_test', include('strategies.nifty_test.urls')),
]
