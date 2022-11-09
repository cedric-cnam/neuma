
import music21 as m21

from fractions import Fraction

'''
 Classes representing musical event (e.g., pairs (duratioin, value)
'''

class Duration:
	'''
		A duration is a fraction of a quarter note
	'''
	
	def __init__(self, numer, denom) :
		self.fraction = Fraction (numer, denom)
		
		# m21 duration is the float obtained from the fraction
		self.m21_duration = m21.duration.Duration(self.fraction)

class Event:
	'''
		Super-class for anything (note, rest, chord) that occurs for a given duration
	'''
	
	# A counter for all events. It consists of i) a global part representing the context
	# (ie, a measure in a part), and ii) a local counter for events met in this context
	counter_context = ""
	counter_event = 0

	@staticmethod 
	def reset_counter(new_context):
		# Initializes the local counter for a new context
		Event.counter_context = new_context
		Event.counter_event = 0
		
	def __init__(self, duration) :
		Event.counter_event += 1
		self.id = f'{Event.counter_context}n{Event.counter_event}'
		self.duration = duration
		self.m21_event = None 

	def is_note(self):
		return False

	def add_articulation (self, art):
		self.m21_event.articulations.append(art.m21_articulation)

class Articulation ():
	"""
		Articulation = some performance indication attached to a note
	"""
	
	STACCATO = "staccato"
	ACCENT = "accent"
	
	def __init__(self, placement, art_type) :
		if art_type == Articulation.STACCATO:
			self.m21_articulation = m21.articulations.Staccato()
		elif art_type == Articulation.ACCENT:
			self.m21_articulation = m21.articulations.Accent()
		else:
			raise Exception ("Unknown articulation type: " + art_type)

		self.m21_articulation.placement = placement
		return

class Note (Event):
	"""
		Representation of a note
	"""
	UNDEFINED_STAFF = 0
	
	ALTER_FLAT = "-"
	ALTER_SHARP = "#"
	ALTER_NATURAL = "n"
	ALTER_NONE = ""
		
	def __init__(self, pitch_class, octave, duration,  alter=ALTER_NONE,
				no_staff=UNDEFINED_STAFF, tied=False) :
		super ().__init__(duration)
		
		self.alter = alter
		self.pitch_class = pitch_class

		pitch_name = pitch_class + alter + str(octave)
		self.alter = alter
		self.m21_event = m21.note.Note(pitch_name)
		self.m21_event.duration = duration.m21_duration
		self.m21_event.id = self.id
		self.no_staff = no_staff
		self.tied = tied
		return
	
	def is_note(self):
		return True
	def get_no_staff(self):
		return self.no_staff
	def get_alter(self):
		return self.alter
	def get_pitch_class(self):
		return self.pitch_class


class Chord (Event):
	"""
		Representation of a chord = a list of notes
	"""
	
	def __init__(self,  duration, no_staff, notes) :
		super ().__init__(duration)
		
		# Create the m21 representation: encode 
		m21_notes = []
		for note in notes:
			m21_notes.append (note.m21_event)
		self.m21_event = m21.chord.Chord(m21_notes)
		self.m21_event.duration = duration.m21_duration
		self.m21_event.id = f'r{Event.counter_event}'
		
		Event.counter_event += 1
		self.no_staff = no_staff
		return
	
	def is_note(self):
		return False
	def get_no_staff(self):
		return self.no_staff


class Rest (Event):
	"""
		Representation of a rest
	"""
	
	def __init__(self,  duration, no_staff) :
		super ().__init__(duration)
		self.m21_event = m21.note.Rest()
		self.m21_event.duration = duration.m21_duration
		self.m21_event.id = f'r{Event.counter_event}'
		Event.counter_event += 1
		self.no_staff = no_staff
		return
	
	def is_note(self):
		return False
	def get_no_staff(self):
		return self.no_staff
