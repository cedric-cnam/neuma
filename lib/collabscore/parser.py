
import  sys, os
# import the logging library
import logging

import json
import jsonref
from pprint import pprint
from jsonref import JsonRef
import jsonschema 

from lib.music.Score import *

# Get an instance of a logger
logger = logging.getLogger(__name__)

class CollabScoreParser:
	"""

		A class to parse a JSON document provided by the OMR tool 
		and to produce encoded scores

	"""

	def __init__(self, schema_file_path, base_uri=""):
		"""
		   Load the schema of OMR json files, for type checking
		   
		   See https://python-jsonschema.readthedocs.io/en/latest/
		"""
		
		sch_file = open(schema_file_path)
		self.schema  = json.load(sch_file)
	
		# The schema containes references to sub-files that need to be solved
		self.resolver = jsonschema.RefResolver(referrer=self.schema, 
										base_uri=base_uri)

		# Check schema via class method call. Works, despite IDE complaining
		self.validator = jsonschema.Draft4Validator (self.schema, resolver=self.resolver)
		
		# Might raise an exception
		jsonschema.Draft4Validator.check_schema(self.schema)
		
		return

	def validate_data (self, json_content):
		# Might raise an exception
		try:
			jsonschema.validate (instance=json_content, 
							schema=self.schema, 
							resolver=self.resolver)
		except jsonschema.ValidationError as ex:
			errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
			raise Exception ("Data  validation error: " + errors)
		except jsonschema.SchemaError as ex:
			raise Exception ("Data  validation error: " + str(ex))

"""
  Utility classes
"""

class OmrScore:
	"""
	  A structured representation of the score supplied by the OMR tool
	"""
	def __init__(self,json_data):
		"""
			Input: a validated JSON object. The method builds
			a representation based on the Python classes
		"""
		self.score_image_url = json_data["score_image_url"]
		self.date = json_data["date"]
		self.pages = []
		
		# Analyze pages
		for json_page in json_data["pages"]:
			self.pages.append(Page(json_page))

	def get_score(self):
		'''
			Builds a score from the Omerized document
		'''
		
		score = Score()
		

		score.add_part("part0")
		return score 

class Zone:
	"""
		A rectangular zone that frames a score graphical element
	"""
	
	def __init__(self,json_zone):
		self.xmin = json_zone[0]
		self.xmax = json_zone[1]
		self.ymin = json_zone[2]
		self.ymax = json_zone[3]

	def __str__(self):
		return f'({self.xmin},{self.ymin},{self.xmax},{self.ymax})'
	
	
class Symbol:
	"""
		An uninterpreted symbol (e.g, a Clef)
	"""
	def __init__(self, json_symbol):
		self.label = json_symbol["label"]
		self.zone = Zone(json_symbol["zone"])
		

	def __str__(self):
		return f'({self.label},{self.zone})'

class Element:
	"""
		An a score element 
	"""
	
	def __init__(self, json_elt):
		self.label = json_elt["label"]
		self.zone = Zone(json_elt["zone"])

	def __str__(self):
		return f'({self.label},{self.zone})'

class Page:
	"""
		An page containing systems
	"""
	
	def __init__(self, json_page):
		self.no_page = json_page["no_page"]
		self.systems=[]
		for json_system in json_page["systems"]:
			self.systems.append(System(json_system))

class System:
	"""
		An sytem containing measures
	"""
	
	def __init__(self, json_system):
		self.id = json_system["id"]
		self.zone = Zone (json_system["zone"])
		self.headers = []
		for json_header in json_system["headers"]:
			self.headers.append(StaffHeader(json_header))
		self.measures = []
		for json_measure in json_system["measures"]:
			self.measures.append(Measure(json_measure))

class Measure:
	"""
		An measure containing voices
	"""
	
	def __init__(self, json_measure):
		self.zone = Zone (json_measure["zone"])
		self.voices =[]
		for json_voice in json_measure["voices"]:
			self.voices.append(Voice(json_voice))

class Voice:
	"""
		An voice containing voice elements
	"""
	
	def __init__(self, json_voice):
		self.items = []
		for json_item in json_voice["elements"]:
			self.items.append(VoiceItem (json_item))
			
		
class VoiceItem:
	"""
		A voice item
	"""
	
	def __init__(self, json_voice_item):
		self.note_attr = None
		self.rest_attr = None
		self.clef_attr = None
		
		self.type = Symbol (json_voice_item["type"])
		self.no_step = json_voice_item["no_step"]
		self.duration = json_voice_item["duration"]
		if "no_group" in json_voice_item:
			self.no_group = json_voice_item["no_group"]
		if "step_duration" in json_voice_item:
			self.step_duration = json_voice_item["step_duration"]
		if "direction" in json_voice_item:
			self.direction = json_voice_item["direction"]
		if "att_note" in json_voice_item:
			self.att_note = NoteAttr (json_voice_item["att_note"])
		if "att_rest" in json_voice_item:
			# NB: using the same type for note heads and rest heads
			self.att_rest = NoteAttr (json_voice_item["att_rest"])
		if "att_clef" in json_voice_item:
			self.att_clef  = Clef (json_voice_item["att_clef"])

	def __str__(self):
		return f'({self.type}, step {self.no_step}, dur. {self.duration})'

class NoteAttr:
	"""
		Note attributes
	"""
	
	def __init__(self, json_note_attr):
		
		self.nb_heads = json_note_attr["nb_heads"]
		self.heads = []
		for json_head in json_note_attr["heads"]:
			self.heads.append(Note (json_head))

	
	def __str__(self):
		return f'({self.type}, step {self.no_step}, dur. {self.duration})'

##############


class Note:
	"""
		Representation of a clef
	"""
	
	def __init__(self, json_note):
		self.tied = False
		self.alter = None

		self.head_symbol =  Symbol (json_note["head_symbol"])
		self.no_staff  = json_note["no_staff"]
		self.height  = json_note["height"]
		
		if "alter" in json_note:
			self.alter = Symbol (json_note["alter"])
		if "tied" in json_note:
			self.tied = json_note["tied"]


class Clef:
	"""
		Representation of a clef
	"""
	
	def __init__(self, json_clef):
		self.symbol =  Symbol (json_clef["symbol"])
		self.no_staff  = json_clef["no_staff"]
		self.height  = json_clef["height"]

class KeySignature:
	"""
		Representation of a key signature
	"""
	
	def __init__(self, json_key_sign):
		self.element =   json_key_sign["element"]
		self.nb_naturals =   json_key_sign["nb_naturals"]
		self.nb_alterations =   json_key_sign["nb_alterations"]

class TimeSignature:
	"""
		Representation of a time signature
	"""
	
	def __init__(self, json_time_sign):
		self.element =   json_time_sign["element"]
		self.time =   json_time_sign["time"]
		self.unit =   json_time_sign["unit"]

class StaffHeader:
	"""
		Representation of a system header
	"""
	
	def __init__(self, json_system_header):
		self.no_staff =json_system_header["no_staff"]
		self.first_bar = Element(json_system_header["first_bar"])

class MeasureHeader:
	"""
		Representation of a measure header
	"""
	
	def __init__(self, json_measure_header):
		self.clef = Clef(json_measure_header["clef"])
		self.key_signature = KeySignature(json_measure_header["key_signature"])
		self.time_signature  = TimeSignature(json_measure_header["time_signature"])

