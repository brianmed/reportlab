###############################################################################
#
#	ReportLab Public License Version 1.0
#
#   Except for the change of names the spirit and intention of this
#   license is the same as that of Python
#
#	(C) Copyright ReportLab Inc. 1998-2000.
#
#
# All Rights Reserved
#
# Permission to use, copy, modify, and distribute this software and its
# documentation for any purpose and without fee is hereby granted, provided
# that the above copyright notice appear in all copies and that both that
# copyright notice and this permission notice appear in supporting
# documentation, and that the name of ReportLab not be used
# in advertising or publicity pertaining to distribution of the software
# without specific, written prior permission.
#
#
# Disclaimer
#
# ReportLab Inc. DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS
# SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS,
# IN NO EVENT SHALL ReportLab BE LIABLE FOR ANY SPECIAL, INDIRECT
# OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
# OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.
#
###############################################################################
#	$Log: sequencer.py,v $
#	Revision 1.8  2000/07/10 11:58:35  andy_robinson
#	Pre-incrementing bug fixed
#
#	Revision 1.7  2000/07/08 07:11:21  andy_robinson
#	Changed to pre-increment
#	
#	Revision 1.6  2000/06/21 19:46:43  rgbecker
#	Added Roman formatters
#	
#	Revision 1.5  2000/06/19 11:14:03  andy_robinson
#	Global sequencer put in the 'story builder'.
#
#	Revision 1.4  2000/06/12 11:27:17  andy_robinson
#	Added Sequencer and associated XML tags
#
#	Revision 1.3  2000/06/11 21:34:01  andy_robinson
#	Largely complete class for numbering lists, figures and chapters
#
#	Revision 1.2  2000/06/09 16:18:19  andy_robinson
#	Doc strings, sequencer
#
#	Revision 1.1  2000/06/01 15:23:06  rgbecker
#	Platypus re-organisation
#
__version__=''' $Id: sequencer.py,v 1.8 2000/07/10 11:58:35 andy_robinson Exp $ '''
"""This module defines a single public class, Sequencer, which aids in
numbering and formatting lists."""
#
# roman numbers conversion thanks to
#
# fredrik lundh, november 1996 (based on a C hack from 1984)
#
# fredrik@pythonware.com
# http://www.pythonware.com
#
_RN_TEMPLATES = [ 0, 01, 011, 0111, 012, 02, 021, 0211, 02111, 013 ]
_RN_LETTERS = "IVXLCDM"
from string import lower

def _format_I(value):
    if value < 0 or value > 3999:
        raise ValueError, "illegal value"
    str = ""
    base = -1
    while value:
        value, index = divmod(value, 10)
        tmp = _RN_TEMPLATES[index]
        while tmp:
            tmp, index = divmod(tmp, 8)
            str = _RN_LETTERS[index+base] + str
        base = base + 2
    return str

def _format_i(num):
	return lower(_format_I(num))

def _format_123(num):
	"""The simplest formatter"""
	return str(num)

def _format_ABC(num):
	"""Uppercase.  Wraps around at 26."""
	n = (num -1) % 26
	return chr(n+65)

def _format_abc(num):
	"""Lowercase.  Wraps around at 26."""
	n = (num -1) % 26
	return chr(n+97)

class _Counter:
	"""Private class used by Sequencer.  Each counter
	knows its format, and the IDs of anything it
	resets, as well as its value. Starts at zero
	and increments just before you get the new value,
	so that it is still 'Chapter 5' and not 'Chapter 6'
	when you print 'Figure 5.1'"""
	def __init__(self):
		self._base = 0
		self._value = self._base
		self._formatter = _format_123
		self._resets = []

	def setFormatter(self, formatFunc):
		self._formatter = formatFunc

	def reset(self, value=None):
		if value:
			self._value = value
		else:
			self._value = self._base

	def next(self):
		self._value = self._value + 1
		v = self._value
		for counter in self._resets:
			counter.reset()
		return v

	def this(self):
		return self._value

	def nextf(self):
		"""Returns next value formatted"""
		return self._formatter(self.next())

	def thisf(self):
		return self._formatter(self.this())

	def chain(self, otherCounter):
		if not otherCounter in self._resets:
			self._resets.append(otherCounter)


class Sequencer:
	"""Something to make it easy to number paragraphs, sections,
	images and anything else.  The features include registering
	new string formats for sequences, and 'chains' whereby
	some counters are reset when their parents.
	It keeps track of a number of
	'counters', which are created on request:
	Usage:
		>>> seq = layout.Sequencer()
		>>> seq.next('Bullets')
		1
		>>> seq.next('Bullets')
		2
		>>> seq.next('Bullets')
		3
		>>> seq.reset('Bullets')
		>>> seq.next('Bullets')
		1
		>>> seq.next('Figures')
		1
		>>>

	"""
	def __init__(self):
		self._counters = {}  #map key to current number
		self._defaultCounter = None

		self._formatters = {
			# the formats it knows initially
			'1':_format_123,
			'A':_format_ABC,
			'a':_format_abc
			}


	def _getCounter(self, counter=None):
		"""Creates one if not present"""
		try:
			return self._counters[counter]
		except KeyError:
			cnt = _Counter()
			self._counters[counter] = cnt
			return cnt



	def this(self, counter=None):
		"""Retrieves counter value but does not increment. For
		new counters, sets base value to 1."""
		if not counter:
			counter = self._defaultCounter
		return self._getCounter(counter).this()

	def next(self, counter=None):
		"""Retrieves the numeric value for the given counter, then
		increments it by one.  New counters start at one."""
		if not counter:
			counter = self._defaultCounter
		return self._getCounter(counter).next()

	def thisf(self, counter=None):
		if not counter:
			counter = self._defaultCounter
		return self._getCounter(counter).thisf()

	def nextf(self, counter=None):
		"""Retrieves the numeric value for the given counter, then
		increments it by one.  New counters start at one."""
		if not counter:
			counter = self._defaultCounter
		return self._getCounter(counter).nextf()

	def setDefaultCounter(self, default=None):
		"""Changes the key used for the default"""
		self._defaultCounter = default

	def registerFormat(self, format, func):
		"""Registers a new formatting function.  The funtion
		must take a number as argument and return a string;
		fmt is a short menmonic string used to access it."""
		self._formatters[format] = func

	def setFormat(self, counter, format):
		"""Specifies that the given counter should use
		the given format henceforth."""
		func = self._formatters[format]
		self._getCounter(counter).setFormatter(func)

	def reset(self, counter=None, base=0):
		if not counter:
			counter = self._defaultCounter
		self._getCounter(counter)._value = base

	def chain(self, parent, child):
		p = self._getCounter(parent)
		c = self._getCounter(child)
		p.chain(c)


	def __getitem__(self, key):
		"""Allows compact notation to support the format function.
		s['key'] gets current value, s['key+'] increments."""
		if key[-1:] == '+':
			counter = key[:-1]
			return self.nextf(counter)
		else:
			return self.thisf(key)

	def format(self, template):
		"""The crowning jewels - formats multi-level lists."""
		return template % self

	def dump(self):
		"""Write current state to stdout for diagnostics"""
		counters = self._counters.items()
		counters.sort()
		print 'Sequencer dump:'
		for (key, counter) in counters:
			print '    %s: value = %d, base = %d, format example = %s' % (
				key, counter.this(), counter._base, counter.thisf())


"""Your story builder needs to set this to"""
_sequencer = None
def getSequencer():
	global _sequencer
	if _sequencer is None:
		_sequencer = Sequencer()
	return	_sequencer

def setSequencer(seq):
	s = _sequencer
	_sequencer = seq
	return s

def test():
	s = Sequencer()
	print 'Counting using default sequence: %d %d %d' % (s.next(),s.next(), s.next())
	print 'Counting Figures: Figure %d, Figure %d, Figure %d' % (
		s.next('figure'), s.next('figure'), s.next('figure'))
	print 'Back to default again: %d' % s.next()
	s.setDefaultCounter('list1')
	print 'Set default to list1: %d %d %d' % (s.next(),s.next(), s.next())
	s.setDefaultCounter()
	print 'Set default to None again: %d %d %d' % (s.next(),s.next(), s.next())
	print
	print 'Creating Appendix counter with format A, B, C...'
	s.setFormat('Appendix', 'A')
	print '    Appendix %s, Appendix %s, Appendix %s' % (
		s.nextf('Appendix'),	s.nextf('Appendix'),s.nextf('Appendix'))

	def format_french(num):
		return ('un','deux','trois','quatre','cinq')[(num-1)%5]
	print
	print 'Defining a custom format with french words:'
	s.registerFormat('french', format_french)
	s.setFormat('FrenchList', 'french')
	print '   ',
	for i in range(1,6):
		print s.nextf('FrenchList'),
	print
	print 'Chaining H1 and H2 - H2 goes back to one when H1 increases'
	s.chain('H1','H2')
	print '    H1 = %d' % s.next('H1')
	print '      H2 = %d' % s.next('H2')
	print '      H2 = %d' % s.next('H2')
	print '      H2 = %d' % s.next('H2')
	print '    H1 = %d' % s.next('H1')
	print '      H2 = %d' % s.next('H2')
	print '      H2 = %d' % s.next('H2')
	print '      H2 = %d' % s.next('H2')
	print
	print 'GetItem notation - append a plus to increment'
	print '    seq["Appendix"] = %s' % s["Appendix"]
	print '    seq["Appendix+"] = %s' % s["Appendix+"]
	print '    seq["Appendix+"] = %s' % s["Appendix+"]
	print '    seq["Appendix"] = %s' % s["Appendix"]
	print
	print 'Finally, string format notation for nested lists.  Cool!'
	print 'The expression ("Figure %(Chapter)s.%(Figure+)s" % seq) gives:'
	print '    Figure %(Chapter)s.%(Figure+)s' % s
	print '    Figure %(Chapter)s.%(Figure+)s' % s
	print '    Figure %(Chapter)s.%(Figure+)s' % s


if __name__=='__main__':
	test()
