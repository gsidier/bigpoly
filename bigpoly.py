import numpy
from poly import Poly, longpoly
from bignum import Bignum, longeval

def uint(sz):
	return numpy.getattr('uint%d' % sz)

class Poly64:
	"""Digits are 64-bit, relying heavily on overflow."""
	type = Poly
	dtype = numpy.int64
	bits = 64
	zero = Poly([])
	max = numpy.iinfo(dtype).max
	@classmethod
	def addc(cls, a, b):
		C = numpy.where(a.coef >= - b.coef, 1, 0)
		return (a + b, C)
	@classmethod
	def mulc(cls, a, b, c):
		half = cls.bits >> 1
		mask = (1 << half) - 1
		a1 = Poly(a.coef >> half)
		a2 = Poly(a.coef & mask)
		b1 = Poly(b.coef >> half)
		b2 = Poly(b.coef & mask)
		a1b1 = a1 * b1
		a1b2 = a1 * b2
		a2b1 = a2 * b1
		a2b2 = a2 * b2
		a1b2_1 = a1b2.coef >> half
		a1b2_2 = a1b2.coef & mask
		a2b1_1 = a2b1.coef >> half
		a2b1_2 = a2b1.coef & mask
		ab22, C1 = cls.addc(a2b2, a1b2_2 << half)
		ab22, C2 = cls.addc(ab22, a2b1_2 << half)
		C = C1 + C2
		ab11 = a1b1.coef << half
		ab11 += C
		ab11 += a1b2_1
		ab11 += a2b1_1
		return ab22, ab11

class HalfInt:
	type = numpy.array
	dtype = numpy.uint
	zero = numpy.zeros(shape=(), dtype=dtype)
	bits = min(i for i in xrange(128) if numpy.iinfo(numpy.uint).max >> i == 0)
	overflow = 1 << (bits - 1)
	half = bits >> 1
	max = 1<< half
	mask = (1 << half) - 1
	@classmethod
	def addc(cls, a, b):
		ab = a + b
		return (ab & cls.mask, ab >> cls.half) 
	@classmethod
	def mulc(cls, a, b, c):
		abc = a * b + c
		return (abc & cls.mask, abc >> cls.half) 

class HalfPoly:
	"""
	This stores half-words in full sized words.
	This makes all the carry handling much easier.
	"""
	class COEF_TYPE(Bignum):
		TYPE = HalfInt

	type = Poly
	dtype = COEF_TYPE.TYPE.dtype
	bits = COEF_TYPE.TYPE.bits
	zero = Poly([])
	ELEM_TYPE = HalfInt
	
	half = bits >> 1
	mask = (1 << half) - 1
	
	max = 1 << half
	
	@classmethod
	def addc(cls, a, b):
		ab = a + b
		hi = cls.type(ab.coef >> cls.half)
		lo = cls.type(ab.coef & cls.mask)
		return lo, hi
	@classmethod
	def mulc(cls, a, b, c):
		abc = a * b + c
		hi = cls.type(abc.coef >> cls.half)
		lo = cls.type(abc.coef & cls.mask)
		return lo, hi
	
class Bigpoly(Bignum):
	
	TYPE = HalfPoly
	
	def __str__(self):
		longcoefs = self.longpoly()
		return "Bigpoly(%s)" % repr(longcoefs.coef)
	
	def __repr__(self):
		return str(self)
	
	def __getitem__(self, i):
		digits = [ D.coef[i] for D in self.digits ]
		if isinstance(i, slice):
			return map(lambda dig: Bignum(* dig), zip(* digits))
		else:
			return Bignum(* digits)
	
	def longpoly(self):
		bigcoefs = zip(* list(P.coef for P in self.digits))
		longcoefs = numpy.array(map(
			lambda digits: longeval(digits, self.TYPE), 
			bigcoefs))
		return longpoly(longcoefs)
	
def bigpoly(coefs):
	return Bigpoly(Poly(numpy.array(coefs, dtype = Bigpoly.TYPE.dtype)))

