
import music21 as m21

from fractions import Fraction

'''
 Classes representing music notation eleements
'''


class Staff:
	'''
		Staff = space where a set of voices from a part (or more?) 
		are displayed. We record in each Staff object the list
		of notational events that occur (clef, signatures, directions, etc.)
	'''
	
	def __init__(self, id_staff) :
		''' 
		   A dictionnary, indexed on measures, that records the clefs
		    used in the staff
		    What if a change occurs in the middle of a measure ? Not
		    supported for the time being. We will need a more powerful
		    notion of 'position'
		'''
		self.id = id_staff
		self.clef_events = {}
		self.time_signature_events = {}
		self.key_signature_events = {}
		self.current_clef = Clef(Clef.TREBLE_CLEF)
		
	def add_clef (self, no_measure, clef):
		self.clef_events[no_measure] = clef
		self.current_clef = clef
	def clef_found_at_measure (self, no_measure):
		return (no_measure in self.clef_events.keys())
	def get_clef (self, no_measure):
		return self.clef_events[no_measure]

class TimeSignature:
	'''
		Represented as a fraction
	'''
	
	def __init__(self, numer, denom) :
		self.fraction = Fraction (numer, denom)
		
		# m21 duration is the float obtained from the fraction
		self.m21_time_signature = m21.meter.TimeSignature(str(self.fraction))

class KeySignature:
	'''
		Represented as the number of sharps (same as music21)
	'''
	
	def __init__(self, nb_sharps=0, nb_flats=0, nb_naturals=0) :
		if nb_sharps > 0:
			self.m21_key_signature = m21.key.KeySignature(nb_sharps)
		elif nb_flats > 0:
			self.m21_key_signature = m21.key.KeySignature((-1) * nb_flats)
		else:
			self.m21_key_signature = m21.key.KeySignature(0)

class Clef:
	'''
		Same as m21
	'''
	
	# DMOS encoding of clefs
	DMOS_TREBLE_CLEF="G"
	DMOS_BASS_CLEF="F"
	DMOS_UT_CLEF="U"

	TREBLE_CLEF = m21.clef.TrebleClef
	ALTO_CLEF = m21.clef.AltoClef
	TENOR_CLEF = m21.clef.AltoClef
	BASS_CLEF = m21.clef.BassClef
	
	def __init__(self, clef_code) :
		if clef_code == self.TREBLE_CLEF:
			self.m21_clef = m21.clef.TrebleClef()
		elif clef_code == self.ALTO_CLEF:
			self.m21_clef = m21.clef.AltoClef()
		elif clef_code == self.TENOR_CLEF:
			self.m21_clef = m21.clef.TenorClef()
		elif clef_code == self.BASS_CLEF:
			self.m21_clef = m21.clef.BassClef()

	@staticmethod 
	def decode_from_dmos (dmos_code, dmos_height):
		#print ("Decode " + dmos_code)
		if dmos_code == Clef.DMOS_TREBLE_CLEF:
			return Clef (Clef.TREBLE_CLEF)
		elif dmos_code == Clef.DMOS_BASS_CLEF:
			return Clef (Clef.BASS_CLEF)
		elif dmos_code == Clef.DMOS_UT_CLEF and dmos_height==3:
			return Clef (Clef.ALTO_CLEF)
		elif dmos_code == Clef.DMOS_UT_CLEF and dmos_height==4:
			return Clef (Clef.TENOR_CLEF)
		else:
			# Should not happen
			logging.error('Unable to decode DMOS code for clef: ' + dmos_code 
						+ " " + str(dmos_height))
			return Clef (TREBLE_CLEF)


	def decode_pitch (self, height):
		''' 
			Given the height on a staff, return the pitch class and octave
		'''
		
		#print ("Decode pitch from height " + str(height) + " and clef " + self.m21_clef)
		# The note of the lowest line
		diatonic_num_base = self.m21_clef.lowestLine
		# We add the line obtained from DMOS
		diatonic_num = diatonic_num_base + height
		pitch = m21.pitch.Pitch() 
		pitch.diatonicNoteNum = diatonic_num
		return (pitch.step, pitch.octave)
