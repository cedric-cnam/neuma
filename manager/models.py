from django.db import models
from datetime import datetime
from urllib.request import urlopen

from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.files.base import ContentFile

from .utils import OverwriteStorage

from django.contrib.auth.models import User
from django.db.models import Count
from django.urls import reverse
#from django.urls import reverse_lazy
from django.conf import settings
import json

from lib.music.Score import *


# For tree models
from mptt.models import MPTTModel, TreeForeignKey

import inspect
from pprint import pprint
import music21 as m21

from xml.dom import minidom
import itertools
import uuid
from zlib import crc32
from hashlib import md5

# Note : we no longer need sklearn nor scipy
from lib.neumautils.stats import symetrical_chi_square
from lib.neumautils.matrix_transform import matrix_transform
from lib.neumautils.kmedoids import cluster
from lib.music.Voice import IncompleteBarsError
import transcription


class Corpus(models.Model):
    title = models.CharField(max_length=255)
    short_title = models.CharField(max_length=255)
    description = models.TextField()
    short_description = models.TextField()
    is_public = models.BooleanField(default=True)
    parent = models.ForeignKey('self', null=True,on_delete=models.PROTECT)
    creation_timestamp = models.DateTimeField('Created',auto_now_add=True)
    update_timestamp = models.DateTimeField('Updated',auto_now=True)
    ref = models.CharField(max_length=255,unique=True)

    def upload_path(self, filename):
        '''Set the path where corpus-related files must be stored'''
        return 'corpora/%s/%s' % (self.ref.replace(settings.NEUMA_ID_SEPARATOR, "/"), filename)
    cover = models.FileField(upload_to=upload_path,null=True,storage=OverwriteStorage())

    def make_ref_from_local_and_parent(self, local_ref, parent_ref):
       """
         Create the corpus reference from the local reference and parent reference
       """
       return parent_ref + settings.NEUMA_ID_SEPARATOR + local_ref

    def __init__(self, *args, **kwargs):
        super(Corpus, self).__init__(*args, **kwargs)

        # Non persistent fields
        self.children = []
        self.matrix = {}

    class Meta:
        db_table = "Corpus"

#        permissions = (
#            ('view_corpus', 'View corpus')
#            ('import_corpus', 'Import corpus'),
#        )

    def __str__(self):              # __unicode__ on Python 2
        return "(" + self.ref + ") " + self.title

    @staticmethod
    def local_ref(ref):
        """
            Get the local ref from the full corpus ref
        """
        if settings.NEUMA_ID_SEPARATOR in ref:
            # Find the last occurrence of the separator
            last_pos = ref.rfind(settings.NEUMA_ID_SEPARATOR)
            return ref[last_pos+1:]
        else:
            # Top-level corpus
            return ref

    @staticmethod
    def parent_ref(ref):
        """
            Get the parent ref from the full corpus ref
        """
        if settings.NEUMA_ID_SEPARATOR in ref:
            # Find the last occurrence of the separator
            last_pos = ref.rfind(settings.NEUMA_ID_SEPARATOR)
            return ref[:last_pos]
        else:
            # Top-level corpus
            return ""

    def get_cover(self):
        """
            Return the corpus cover if exists, else take the parent cover (recursively)
        """
        if self.cover != "":
            return self.cover;
        elif self.parent is not None:
            return self.parent.get_cover()
        else:
            # Should not happen: a top level corpus without image
            return ""

    def get_url(self):
        """
          Get the URL to the Web corpus page, taken from urls.py
        """
        return reverse('home:corpus', args=[self.ref])

    def load_from_dict(self, dict_corpus):
        """Load content from a dictionary. used to migrate from Neuma/CouchDB"""
        self.ref = dict_corpus["id"]
        self.title = dict_corpus["title"]
        self.short_title = dict_corpus["shortTitle"]
        self.description = dict_corpus["description"]
        self.is_public = dict_corpus["isPublic"]
        self.short_description = dict_corpus["shortDescription"]

        # Take the cover image
        if dict_corpus["cover"] is not None:
            file_temp = NamedTemporaryFile()
            f = urlopen(dict_corpus["cover"])
            content = f.read()
            file_temp.write(content)
            file_temp.flush()
            self.cover.save("cover.jpg", File(file_temp))
        else:
            # Good to know: sets the file field to blank string
            self.cover = None

        return

    def get_children(self, recursive=True):
        self.children = Corpus.objects.filter(parent=self)
        for child in self.children:
            child.get_children(recursive)
        return self.children

    def get_direct_children(self):
        return self.get_children(False)

    def get_nb_children(self):
        return Corpus.objects.filter(parent=self).count()

    def get_nb_grammars(self):
        return transcription.models.Grammar.objects.filter(corpus=self).count()
    
    def get_grammars(self):
        return transcription.models.Grammar.objects.filter(corpus=self).order_by('name')

    def get_nb_opera(self):
        return Opus.objects.filter(corpus=self).count()
    def get_nb_opera_and_descendants(self):
        return Opus.objects.filter(ref__startswith=self.ref).count()

    def get_opera(self):
        return Opus.objects.filter(corpus=self).order_by('ref')

    def generate_sim_matrix(self):
        ''' Compute distance matrix and store them in database in form
            of triplets (opus,opus,distance) '''

        all_pairs = itertools.combinations(self.get_opera(),2)
        i,l = 0, len(list(all_pairs))

        missing_score = {}
        error_status = {}

        for pair in itertools.combinations(self.get_opera(),2):
            #print(str(i)+'/'+str(l),end="    ")
            if pair[0].ref != pair[1].ref:
                for crit in SimMeasure.objects.order_by('code'):#does this work without @/map ?
                    self.matrix[crit] = {} # temp local storage

#                    print ("Process opus " + matrix.opus1.ref + " and opus " + matrix.opus2.ref)
                    try:
                        hist1 = pair[0].get_histograms(crit)#.values() 
                    except LookupError:
                        missing_score[pair[0].ref] = True
                        continue                
                    except Exception as e:
                        error_status[pair[0].ref] = True
                        continue                                        

                    try:
                        hist2 = pair[1].get_histograms(crit)#.values()
                    except LookupError:
                        missing_score[pair[1].ref] = True
                        continue                
                    except Exception as e:
                        error_status[pair[1].ref] = True
                        continue                          

                    # Make the two histogram have the same keys
                    # This solves rhythms "problem"
                    for a in set(hist1.keys()).union(set(hist2.keys())):
                        if a not in hist1:
                            hist1[a] = 0
                        if a not in hist2:
                            hist2[a] = 0
              

                    value = symetrical_chi_square(list(hist1.values()),list(hist2.values()))

                    # Note : we update or create value to avoid duplication of matrix in DB
                    if value != 'nan':
                        SimMatrix.objects.update_or_create(
                            sim_measure = crit,
                            opus1 = pair[0],
                            opus2 = pair[1],
                            value = value
                        )
                        SimMatrix.objects.update_or_create(
                            sim_measure = crit,
                            opus1 = pair[1],
                            opus2 = pair[0],
                            value = value
                        )
            i+=1
            #print("\r",end="")
        print(str(l-len(error_status)-len(missing_score))+"/"+str(l)+" combination computed")
        print("Missing score for "+str(len(missing_score))+" opera : ")
        print(",".join(missing_score.keys()))
        print("Error processing "+str(len(error_status))+" opera : ")
        print(",".join(error_status.keys()))

    def get_matrix_data(self, measure):
        # measure = SimMeasure.objects.get(code=measure)
        data = SimMatrix.objects.filter(sim_measure=measure,
                                        opus1__corpus=self,
                                        opus2__corpus=self)
        return data

    def has_matrix(self,measure):
        return len(self.get_matrix_data(measure))>0

    def generate_kmeans(self,measure_name,nb_class):

        # Prevents crash if distances haven't been computed for this corpus
        if not self.has_matrix(measure_name):
            return []


        try:
            measure = SimMeasure.objects.get(code=measure_name)
        except:
            print('Invalid measure given "'+measure_name+'"')
            return
        
        q1 = SimMatrix.objects.filter(sim_measure=measure,
                opus1__corpus=self).values_list('opus1','opus2','value')
        q2 = SimMatrix.objects.filter(sim_measure=measure,
                opus2__corpus=self).values_list('opus1','opus2','value')

        # x + (y-x)   :: note : this is missing on neighbor query !!!
        all_distances = list(q1) + list(set(q1) - set(q2))

        # Mapping distances to matrix
        distances , map_ids = matrix_transform(all_distances)

        # Computing clusters / medoids
        clusters , medoids = cluster(distances,int(nb_class))


        
    #    pprint(clusters)
    #    pprint(medoids)
#        pprint(list(map(lambda x:map_ids[x],clusters)))
    #    pprint(list(map(lambda x:map_ids[x],medoids)))


 #        SimMatrix.objects.update_or_create(
 #           sim_measure = crit,
 #           corpus = self,
 #           value = value
 #       )
 
        # ok FIXME : how should we store kmedoids / clusters in DB ?
        # --> how to display them on corpus page ?


        # Return n medoids
        return list(map(lambda x:map_ids[x],medoids))

    def get_medoids(self,measure,k):
        x = list(map(lambda x:Opus.objects.filter(id=x)[0],self.generate_kmeans(measure,k)))
        pprint(x)
        return x


####################################################

class Opus(models.Model):
    corpus = models.ForeignKey(Corpus,on_delete=models.PROTECT)
    title = models.CharField(max_length=255)
    lyricist = models.CharField(max_length=255,null=True, blank=True)
    composer = models.CharField(max_length=255,null=True, blank=True)
    ref = models.CharField(max_length=255,unique=True)
    external_link  = models.CharField(max_length=255,null=True, blank=True)
    
    # .Files names
    FILE_NAMES = {"score.xml": "musicxml", "mei.xml": "mei","score.png": "png",
                  "preview.png": "preview", "score.pdf": "pdf", "preview.ly": "lilypreview",
                  "score.ly": "lilypond", "score.midi": "midi", "summary.json": "summary",
                  "record.mp3": "record"}

    def statsDic(opus):
        """ produces a dic with features"""
        stats = StatsDesc(opus)
        dico = stats.computeStats()
        return dico

    def upload_path(self, filename):
        '''Set the path where opus-related files must be stored'''
        return 'corpora/%s/%s' % (self.ref.replace(settings.NEUMA_ID_SEPARATOR, "/"), filename)

    def __init__(self, *args, **kwargs):
        super(Opus, self).__init__(*args, **kwargs)
        # Non persistent fields
        # self.stats = self.statsDic()
        self.histogram_cache={}

    # List of files associated to an Opus
    musicxml = models.FileField(upload_to=upload_path,null=True,storage=OverwriteStorage())
    mei = models.FileField(upload_to=upload_path,null=True,storage=OverwriteStorage(), max_length=255)
    png = models.FileField(upload_to=upload_path,null=True,storage=OverwriteStorage())
    preview = models.FileField(upload_to=upload_path,null=True,storage=OverwriteStorage())
    pdf = models.FileField(upload_to=upload_path,null=True,storage=OverwriteStorage())
    lilypond = models.FileField(upload_to=upload_path,null=True,storage=OverwriteStorage())
    lilypreview = models.FileField(upload_to=upload_path,null=True,storage=OverwriteStorage())
    midi = models.FileField(upload_to=upload_path,null=True,storage=OverwriteStorage())
    summary = models.FileField(upload_to=upload_path,null=True,storage=OverwriteStorage())
    record = models.FileField(upload_to=upload_path,null=True,blank=True,storage=OverwriteStorage())

    class Meta:
        db_table = "Opus"
    
    def get_url(self):
        """
          Get the URL to the Web opus page, taken from urls.py
        """
        return reverse('home:opus', args=[self.ref])

    def local_ref(self):
       """
         The ref of the Opus inside its Corpus
       """
       last_pos = self.ref.rfind(settings.NEUMA_ID_SEPARATOR)
       return self.ref[last_pos+1:]

    def add_meta (self, mkey, mvalue):
        """Add a (key, value) pair as an ad-hoc attribute"""
        
        # Search if exists
        try:
            meta_pair = OpusMeta.objects.get(opus=self,meta_key=mkey)
        except OpusMeta.DoesNotExist as e:
            meta_pair = OpusMeta(opus=self,meta_key=mkey, meta_value=mvalue)
            meta_pair.save()

    def get_metas (self):
        """Return the list of key-value pairs"""
        metas = []
        for m in OpusMeta.objects.filter(opus=self):
            m.displayed_label = OpusMeta.META_KEYS[m.meta_key]["displayed_label"]
            metas.append (m)
        return metas

        
    def load_from_dict(self, corpus, dict_opus, files={}, opus_url=""):
        """Load content from a dictionary.

        The dictionary is commonly a decrypted JSON object, coming
        either from the Neuma REST API or from ElasticSearch

        """
        # The id can be named id or _id
        if ("id" in dict_opus.keys()):
            self.ref = dict_opus["id"].strip()
        elif ("_id" in dict_opus.keys()):
            self.ref = dict_opus["_id"].strip()
        else:
            raise  KeyError('Missing id field in an Opus dictionary')

        self.title = dict_opus["title"]

        if ("lyricist" in dict_opus.keys()):
            if (dict_opus["lyricist"] != None):
                self.lyricist = dict_opus["lyricist"]
        if ("composer" in dict_opus.keys()):
            if (dict_opus["composer"] != None):
                self.composer = dict_opus["composer"]
        if ("metas" in dict_opus.keys()):
            if (dict_opus["metas"] != None):
                for m in dict_opus["metas"]:
                    add_meta (m.meta_key, m.meta_value)
        self.corpus = corpus

        # Get the Opus files
        for fname, desc  in files.items():
            if (fname in Opus.FILE_NAMES ):
                print ("Found " + fname + " at URL " + opus_url + fname)
                # Take the score
                file_temp = NamedTemporaryFile()
                f = urlopen(opus_url + fname)
                content = f.read()
                file_temp.write(content)
                file_temp.flush()
                getattr(self, Opus.FILE_NAMES[fname]).save(fname, File(file_temp))

        # Get the sequence file if any
        if opus_url != "":
            print ("Try to import sequence file")
            try:
                f = urlopen(opus_url + "sequence.json")
                content = f.read().decode("utf-8")
                # test that we got it
                jseq = json.loads(content)
                if "status" in jseq.keys():
                    print ("Something wrong. Received message: " + jseq["message"])
                else:
                    self.music_summary = content
            except:
                print("Something wrong when getting "  + opus_url + "sequence.json")

        return

    def get_score(self):
        """Get a score object from an XML document"""
        score = Score()
        # Try to obtain the MEI document, which contains IDs
 
        if self.mei :
            #print ("Load from MEI")
            score.load_from_xml(self.mei.path, "mei")
            return score
        elif self.musicxml :
            #print ("Load from MusicXML")
            score.load_from_xml(self.musicxml.path, "musicxml")
            return score
        else:
            raise LookupError ("Opus " + self.ref + " doesn't have any XML file attached")

    def freeze(self,filepath="./"):
        # http://web.mit.edu/music21/doc/moduleReference/moduleConverter.html#music21.converter.freeze
        try:
            score = self.get_score().m21_score
            path = filepath
            m21.converter.freeze(score, fp=path)
            # print("Opus "+self.ref+" was serialized at "+path)
        except:
            print("something went wrong in serializing with m21")
        return filepath

    def unfreeze(self,filepath="./"):
        score = m21.converter.thaw(filepath)
        return score


    @staticmethod
    def createFromMusicXML(corpus, reference, mxml_content):
        """Create a new Opus by getting metadata as much as possible from the XML file"""
        opus_ref = corpus.ref + settings.NEUMA_ID_SEPARATOR + reference
        try:
            opus = Opus.objects.get(ref=opus_ref)
        except Opus.DoesNotExist as e:
            opus = Opus()
        
        opus.corpus = corpus
        opus.ref = opus_ref
        opus.title = reference # Temporary
        opus.musicxml.save("score.xml", ContentFile(mxml_content))
        
        doc = minidom.parseString(mxml_content)
        titles = doc.getElementsByTagName("movement-title")
        for title in titles:
            for txtnode in title.childNodes:
                opus.title = str(txtnode.data)
                print ("Found title metadata : " + opus.title)
                break
            break
        
        if opus.title == reference:
            # Try to find metadata in the XML file with music21
            score = opus.get_score()
        
            if score.get_title() != None and len(score.get_title()) > 0:
                opus.title = score.get_title()
            if score.get_composer() != None and len(score.get_composer()) > 0:
                opus.composer = score.get_composer()

        return opus
    
    def __str__(self):              # __unicode__ on Python 2
        return self.title

    def get_histograms(self,measure):
        """Compute the histogram feature from some measure
           and put it in the cache. Further requests of the same
           feature will find it in the cache"""
        measure=str(measure)

        if measure in self.histogram_cache and self.histogram_cache[measure]:
            # The histogram already exists
            return self.histogram_cache[measure]
        else:
            # We need to compute it
            score = self.get_score()
            voices = score.get_all_voices()
            if not len(voices):
                raise LookupError

            voice = voices[0] # FIXME
            if measure == 'pitches':
                self.histogram_cache[measure] = voice.get_pitches_norm()
            elif measure == 'degrees':
                self.histogram_cache[measure] = voice.get_degrees_norm()
            elif measure == 'intervals':
                self.histogram_cache[measure] = voice.get_intervals_norm()
            elif measure == 'rhythms':
                self.histogram_cache[measure] = voice.get_rhythmicfigures_norm()
            else:
                print("WARNING : unknown measure " + str(measure))#raise UnknownSimMeasure(measure)

            return self.histogram_cache[measure]

    def delete_index(self):
        #
        #   Delete opus in ElasticSearch
        #   Called by signal delete_index_opus
        #
        opus = OpusIndex.get(id=self.id, index=settings.ELASTIC_SEARCH["index"])
        result = opus.delete()
        return result

    def to_json(self):
        """
          Create a dictionary that can be used for JSON exports
        """
        metas = []
        for meta in self.get_metas ():
            metas.append({"meta_key": meta.meta_key, "meta_value": meta.meta_value})
        return {"id": self.ref, 
                 "title": self.title, "composer": self.composer, 
                 "lyricist": self.lyricist, 
                 "corpus": self.corpus.ref,
                 "meta_fields": metas}


class OpusMeta(models.Model):
    opus = models.ForeignKey(Opus,on_delete=models.CASCADE)
    meta_key = models.CharField(max_length=255)
    meta_value = models.TextField()
    
    # 
    # List of allowed meta keys, 
    MK_OFFICE = "office"
    MK_FETE = "fete"
    MK_MODE = "mode"
    MK_GENRE = "genre"
    MK_SOLENNITE = "solennite"
    MK_TEXTE = "texte"
    
    # Descriptive infos for meta pairs
    META_KEYS = {
        MK_OFFICE: {"displayed_label": "Office"},
        MK_FETE: {"displayed_label": "Fête"},
        MK_MODE: {"displayed_label": "Mode"},
        MK_GENRE: {"displayed_label": "Genre"},
        MK_SOLENNITE: {"displayed_label": "Degré de solennité"},
        MK_TEXTE: {"displayed_label": "Texte"},
                 }

    def __init__(self, *args, **kwargs):
        super(OpusMeta, self).__init__(*args, **kwargs)

    class Meta:
        db_table = "OpusMeta"


class Descriptor(models.Model):
    '''A descriptor is a textual representation for some musical feature, used for full text indexing'''
    opus = models.ForeignKey(Opus,on_delete=models.CASCADE)
    part = models.CharField(max_length=30)
    voice = models.CharField(max_length=30)
    type = models.CharField(max_length=30)
    value = models.TextField()

    class Meta:
        db_table = "Descriptor"

    def to_dict(self):
        return dict(part=self.part, voice=self.voice, value=self.value)

    def __str__(self):
        return self.type + " " + str(self.opus.ref) + " " + str(self.opus.corpus)


class Bookmark(models.Model):
    '''Record accesses from user to opera'''
    opus = models.ForeignKey(Opus,on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    timestamp = models.DateTimeField('Created', auto_now_add=True)

    class Meta:
        db_table = "Bookmark"

        
class Upload (models.Model):
    '''Storage and desription of ZIP file containing
    a list of XML pieces to be imported in a corpus'''
    corpus = models.ForeignKey(Corpus,on_delete=models.PROTECT)
    description =   models.TextField()
    creation_timestamp = models.DateTimeField('Created', auto_now_add=True)
    update_timestamp = models.DateTimeField('Updated', auto_now=True)

    def upload_path(self, filename):
        '''Set the path where upload files must be stored'''
        corpus_ref = self.corpus.ref.replace(settings.NEUMA_ID_SEPARATOR, "-")
        timestamp = datetime.utcnow().strftime("%Y_%m_%d_%H_%M_%S_%f")
        return 'uploads/' + corpus_ref + '-' + timestamp  + '.zip'
    zip_file = models.FileField(upload_to=upload_path,null=True,storage=OverwriteStorage())

    class Meta:
        db_table = "Upload"    

    def __str__(self):  # __unicode__ on Python 2
        return "(" + self.corpus.ref + ") " + self.zip_file.name

class Audio (models.Model):
    '''Storage of audio files associated to an opus'''
    opus = models.ForeignKey(Opus,on_delete=models.PROTECT)
    filename = models.TextField()
    description =   models.TextField()
    creation_timestamp = models.DateTimeField('Created', auto_now_add=True)
    update_timestamp = models.DateTimeField('Updated', auto_now=True)

    def upload_path(self, filename):
        '''Set the path where audio files must be stored'''
        audio_ref = self.opus.ref.replace(settings.NEUMA_ID_SEPARATOR, "-")
        return 'audio_files/' + audio_ref + '/' + self.filename
    audio_file = models.FileField(upload_to=upload_path,null=True,storage=OverwriteStorage())

    class Meta:
        db_table = "Audio"    

    def __str__(self):  # __unicode__ on Python 2
        return "(" + self.opus.ref + ") " + self.filename


class SimMeasure(models.Model):
    code = models.CharField(max_length=255,unique=True)

    def __init__(self, *args, **kwargs):
        super(SimMeasure, self).__init__(*args, **kwargs)

    class Meta:
        db_table = "SimMeasure"
        
    def __str__(self):
        return  self.code 


class SimMatrix(models.Model):
    sim_measure = models.ForeignKey(SimMeasure,on_delete=models.PROTECT)
    opus1 = models.ForeignKey(Opus, related_name="%(app_label)s_%(class)s_opus1",on_delete=models.PROTECT)
    opus2 = models.ForeignKey(Opus, related_name="%(app_label)s_%(class)s_opus2",on_delete=models.PROTECT)
    value = models.FloatField()

    def __init__(self, *args, **kwargs):
        super(SimMatrix, self).__init__(*args, **kwargs)

    class Meta:
        db_table = "SimMatrix"


class Kmeans(models.Model):
    tag = models.CharField(max_length=255,unique=True)
    corpus = models.ForeignKey(Corpus,on_delete=models.PROTECT)
    group = models.IntegerField()
    measure = models.ForeignKey(SimMeasure,on_delete=models.PROTECT)

    class Meta:
        db_table = "Kmeans"


class Histogram(object):
    ''' Represents an histogram, ready to be displayed on stat page '''
    def __init__(self,data,labels,title,labelling_closure=None):
        self.data = data
        self.labels = labels
        self.title = title
        if labelling_closure:
            self.labelling_closure = labelling_closure
        else:
            self.labelling_closure = lambda x:str(x)

        # Color is completely pseudo-randomly generated.
        # Hopefully the result is not that bad.
        # We can still add salt to change them.
        self.color = md5(str(self.title).encode('utf-8')).hexdigest()[0:6]

    def generate_uid(self):
        return self.title+str(uuid.uuid4())


class UnknownSimMeasure(Exception):
    pass


class AnalyticModel(models.Model):
    """Analytic model = a set of concepts used to interpret a music language"""
    code = models.CharField(max_length=30,unique=True)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()

    class Meta:
        db_table = "AnalyticModel"
        
    def __str__(self):              # __unicode__ on Python 2
        return self.name


class AnalyticConcept(MPTTModel):
    model = models.ForeignKey(AnalyticModel,on_delete=models.PROTECT)
    code = models.CharField(max_length=30,unique=True)
    name = models.CharField(max_length=50, unique=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True,on_delete=models.PROTECT)
    description = models.TextField()
    display_options = models.CharField(max_length=255,  default='#ff0000')
    icon = models.TextField(default='')

    class Meta:
        db_table = "AnalyticConcept"

    def __str__(self):              # __unicode__ on Python 2
        return self.name

    class MPTTMeta:
        order_insertion_by = ['name']


class Annotation(models.Model):
    '''An annotation qualifies a fragment of a score with an analytic concept'''
    opus = models.ForeignKey(Opus,on_delete=models.PROTECT)
    # Analytic concept: for the moment, a simple code. See how we can do better
    analytic_concept = models.ForeignKey(AnalyticConcept,on_delete=models.PROTECT)
    # reference to the element being annotated, in principle an xml:id
    ref = models.TextField(default="")
    # The fragment is represented by a json array of notes ids< OBSOLETE.
    fragment = models.TextField()
    # Where to position the annotation. Always given by the id of a note
    offset = models.TextField(default="")
    # Music21 offset
    m21_offset = models.TextField(default="")
    # Whether the annotation is manual or not 
    is_manual = models.BooleanField(default=False)
    # The user that creates the annotation
    user = models.ForeignKey(User, null=True,on_delete=models.PROTECT)
    # Comment made by the user
    comment = models.TextField(null=True, default="")
    # XML fragment (alternate version proposed by the user)
    xml_fragment = models.TextField(null=True, default="")
    # Name and version of the model used for analysis
    model_ref = models.TextField(default="")

    # Creation / update dates
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = "Annotation"
        
    def create_from_web_input (self, form_data):
        print ("Annotation from JSON")
        print (str(form_data))
        
