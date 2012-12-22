import sys

class Int:
	type = int
	max = sys.maxint
	zero = 0
	addc = classmethod(lambda cls,a,b: (int((a + b) % cls.max), 1 if a >= cls.max - b else 0))
	"""
	@classmethod
	def addc(cls, a, b, c):
		abc = a + b + c
		return int(abc % cls.max), 1 if abc >= cls.max else 0
	"""
	@classmethod
	def mulc(cls, a, b, c):
		abc = a * b + c
		return int(abc % cls.max), int(abc / cls.max)
	
class Bit(Int):
	max = 2

class Digit(Int):
	max = 10

class Bignum(object):
	TYPE = Int
	"A big number class supporting (almost) any digit type"
	def __init__(self, *digits):
		self.digits = list(digits)
	def __add__(self, them):
		zero, addc = self.TYPE.zero, self.TYPE.addc
		if not hasattr(them, 'TYPE'): # not a BigNum?
			them = type(self)(them) # convert to Bignum
		n = max(len(self.digits), len(them.digits))
		digits1 = self.digits + [ zero ] * (n - len(self.digits))
		digits2 = them.digits + [ zero ] * (n - len(them.digits))
		digits = [ ]
		c = zero
		for d1, d2 in zip(digits1, digits2):
			d, c0 = addc(d1, d2)
			d, c = addc(d, c)
			c += c0
			"""d, c = addc(d1, d2, c)"""
			digits.append(d)
		if c != zero:
			digits.append(c)
		return type(self)(*digits)
	def scale(self, x):
		zero = self.TYPE.zero
		mulc = self.TYPE.mulc
		digits = [ ]
		c = zero
		for d in self.digits:
			m, c = mulc(d, x, c)
			digits.append(m)
		if c != zero:
			digits.append(c)
		return type(self)(*digits)
	def shift(self, n):
		return type(self)(*([ self.TYPE.zero ] * n + self.digits))
	def __mul__(self, them):
		if not hasattr(them, 'TYPE'):
			return self.scale(them)
		res = type(self)()
		for (k, d) in enumerate(them.digits):
			res = res + self.scale(d).shift(k)
		return res
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
	def __repr__(self):
		return "%s(%s)" % (type(self).__name__, ', '.join(map(repr, self.digits)))

class Digits(Bignum):
	def __str__(self):
		return ''.join(map(str, self.digits[::-1]))

class Binary(Digits):
	TYPE = Bit

class Decimal(Digits):
	TYPE = Digit

def longeval(digits, TYPE):
	return sum(
		long(TYPE.max) ** i * long(d)
		for (i, d) in enumerate(digits)
	)

