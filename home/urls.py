from django.conf.urls import url
from django.views.generic import TemplateView
from . import views

from neumautils.views import NeumaView
from .views import *

app_name="home"
urlpatterns = [
    url(r'^$', NeumaView.as_view(template_name="home/index.html"), name='index'),
   url(r'wildwebmidi.data', views.wildwebdata, name='wildwebdata'),
#
#   Philippe: what is this ???
#   url (r'(.+\.data)$', views.wildwebdata, name='coco'),

    url(r'^presentation$', NeumaView.as_view(template_name="home/presentation.html"), name='presentation'),
    url(r'^services$', NeumaView.as_view(template_name="home/services.html"), name='services'),
    url(r'^collections$', NeumaView.as_view(template_name="home/collections.html"), name='collections'),
    url(r'^contact$', NeumaView.as_view(template_name="home/contact.html"), name='contact'),
     url(r'^test', NeumaView.as_view(template_name="home/test.html"), name='test'),
   url(r'^auth', AuthView.as_view(template_name="home/index.html"), name='auth'),
   url(r'^form_login', TemplateView.as_view(template_name="home/form_login.html"), name='form_login'),
    url(r'^transcription', NeumaView.as_view(template_name="transcription/index.html"), name='transcription'),
    url(r'^keyboard', TemplateView.as_view(template_name="home/keyboard.html"), name='keyboard'),
    # ex: /main/corpus/sequentia/
    url(r'^corpus/(?P<corpus_ref>.+)/_export_zip/$', views.export_corpus_as_zip , name='corpus_export_zip'),
    url(r'^corpus/(?P<corpus_ref>.+)/_upload_zip/$', views.upload_corpus_zip , name='upload_corpus_zip'),
    url(r'^corpus/(?P<corpus_ref>.+)/_create_child/$', CorpusEditView.as_view(template_name="home/corpus_edit.html"), name='create_corpus_child'),
    url(r'^corpus/(?P<corpus_ref>.+)/_add_opus/$', views.add_opus , name='add_opus'),
    url(r'^corpus/(?P<corpus_ref>.+)/$', CorpusView.as_view(template_name="home/corpus.html"), name='corpus'),
    url(r'^show_licence/(?P<licence_code>.+)/$', views.show_licence , name='show_licence'),
    url(r'^opus/(?P<opus_ref>.+)/_edit/$', views.edit_opus , name='edit_opus'),
	url(r'^opus/(?P<opus_ref>.+)/_export_zip/$', views.export_opus_as_zip , name='opus_export_zip'),
    url(r'^opus/(?P<opus_ref>.+)/(?P<pattern>.*)/$', OpusView.as_view(template_name="home/opus.html"), name='opus'),
    url(r'^opus/(?P<opus_ref>.+)/$', OpusView.as_view(template_name="home/opus.html"), name='opus'),
    url(r'^zoom/(?P<score_url>.+)/$', NeumaView.as_view(template_name="home/zoom.html"), name='zoom'),
    url(r'^search', SearchView.as_view(template_name="home/search.html"), name='search'),
    url(r'^structsearch', StructuredSearchView.as_view(template_name="home/structsearch.html"), name='structsearch'),
]
