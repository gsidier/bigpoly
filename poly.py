import numpy
from copy import copy

class Poly(object):
	def __init__(self, coef):
		self.coef = numpy.array(coef)
	def __add__(self, them):
		a, b = self.coef, them.coef
		if len(a) < len(b):
			b, a = a, b
		a = copy(a)
		a[:len(b)] += b
		return type(self)(a)
	def __mul__(self, them):
		return type(self)(numpy.convolve(self.coef, them.coef))
	def __pow__(self, n):
		a = self
		r = a if n & 1 else None
		n >>= 1
		while n:
			a = a * a
			if n & 1:
				r = r * a if r else a
			n >>= 1
		return r
	def normalize(self):
		if len(self.coef) == 0 or self.coef[-1] != 0:
			return self
		nonzero = list(i for i in xrange(len(self.coef)) if self.coef[i] != 0)
		n = 1 + max(nonzero) if nonzero else 0
		return type(self)(self.coef[:n])
	def __eq__(self, them):
		lhs = self.normalize().coef
		rhs = them.normalize().coef
		return (lhs.size == rhs.size) and numpy.all(lhs != rhs)
	def __ne__(self, them):
		lhs = self.normalize().coef
		rhs = them.normalize().coef
		return (lhs.size != rhs.size) or numpy.any(lhs != rhs)
	def __repr__(self):
		return "%s(%s)" % (type(self).__name__, repr(self.coef))


def longpoly(coef):
	return Poly(numpy.array(map(long, coef), dtype=object))

