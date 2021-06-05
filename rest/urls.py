from rest_framework import routers
from . import views
from django.conf.urls import include, url
from django.views.decorators.csrf import csrf_exempt

from django.urls import  path

from .views import *


from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from rest_framework.documentation import include_docs_urls

#router = routers.DefaultRouter()

#router.register(r'source', views.Source, base_name='rest_source')
app_name="rest"


schema_view = get_schema_view(
   openapi.Info(
      title="Neuma REST API",
      default_version='v1',
      description="List and usage of Neuma REST services",
   ),
   public=False,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    # Welcome message
     path('', views.welcome, name='welcome'),

   #### Swagger documentation
   path('apidoc/', include_docs_urls(title='Neuma REST API documentation')),
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
  path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
   path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    ###############
    ## MISC SERVICE
    ###############
    url(r'^misc/user/$', views.handle_user_request, name='handle_user_request'),
    ###############
    ## META DATA
    ###############
    url(r'^analysis/_models/(?P<model_code>.+)/_concepts/_all/$', views.handle_concepts_request, name='handle_concepts_request'),
    url(r'^analysis/_models/(?P<model_code>.+)/_concepts/(?P<concept_code>.+)/_all/$', views.handle_concepts_request, name='handle_concepts_request'),
    #url(r'^analysis/models/(?P<model_code>.+)/concepts/(?P<encoding>.+)/$', views.handle_concepts_request, name='handle_concepts'),
    ################
    # ANNOTATIONS
    ################
    # PUT a new annotation
    url (r'^collections/(?P<full_neuma_ref>(.*))/_annotations/$', views.handle_annotation_request, name='handle_put_annotation_request'),
    # Compute annotations for an Opus and a model
    url(r'^collections/(?P<full_neuma_ref>(.*))/_annotations/(?P<model_code>[-\w]+)/_compute/$', views.compute_annotations, name='compute_annotations'),
    # Get the list of annotations for an object and a model
    url (r'^collections/(?P<full_neuma_ref>(.*))/_annotations/(?P<model_code>[-\w]+)/_all/$', views.handle_annotations_request, name='handle_annotations_model_request'),
    # Get the list of annotations for an object, a model and a concept
    url (r'^collections/(?P<full_neuma_ref>(.*))/_annotations/(?P<model_code>[-\w]+)/(?P<concept_code>.+)/_all/$', views.handle_annotations_request, name='handle_annotations_request'),
    # Get/Post a specific annotation
    url (r'^collections/(?P<full_neuma_ref>(.*))/_annotations/(?P<annotation_id>[-\w]+)/$', views.handle_annotation_request, name='handle_annotation_request'),
    #################
    # Transcription
    #################
    # Access to a grammar by its name
    path('transcription/_qparse/', views.qparse, name='grammars'),
    path('transcription/grammars/', views.grammars, name='grammars'),
    path('transcription/grammars/<str:grammar_name>/', views.grammar, name='grammar'),

    ################
    # OPUS / CORPUS
    ################    
    path('collections/', views.welcome_collections, name='welcome_collections'),
    url(r'^collections/_corpora/$', views.TopLevelCorpusList.as_view(), name='handle_tl_corpora_request'),
    url(r'^collections/(?P<full_neuma_ref>(.+))/_corpora/$', views.CorpusList.as_view(), name='handle_corpora_request'),
    url(r'collections/(?P<full_neuma_ref>(.*))/_opera/$', views.handle_opera_request, name='handle_opera_request'),
    url(r'collections/(?P<full_neuma_ref>(.*))/_files/$',views.handle_files_request, name='handle_files_request'),
    url(r'collections/(?P<full_neuma_ref>(.*))/_uploads/(?P<upload_id>(.*))/_import/$',views.handle_import_request, name='handle_import_request'),
    # Request for a specific file
    url (r'^collections/(?P<full_neuma_ref>(.*))/*.xml$', views.handle_neuma_ref_request, name='handle_files_reauest'),
    # Generic request to a corpus or an opus 
    url (r'^collections/(?P<full_neuma_ref>(.*))/$', views.handle_neuma_ref_request, name='handle_neuma_ref_request'),
]