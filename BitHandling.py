import logging

class BitHandling:

	def __init__(self):
		self.logger = logging.getLogger('ws28xx.BitHandling')
		self.logger.debug("")

	# testBit() returns a nonzero result, 2**offset, if the bit at 'offset' is one.
	def testBit(self,int_type, offset):
		mask = 1 << offset
		return(int_type & mask)

	# setBit() returns an integer with the bit at 'offset' set to 1.
	def setBit(self,int_type, offset):
		mask = 1 << offset
		return(int_type | mask)

	# setBitVal() returns an integer with the bit at 'offset' set to 1.
	def setBitVal(self,int_type, offset, val):
		mask = val << offset
		return(int_type | mask)
	
	# clearBit() returns an integer with the bit at 'offset' cleared.
	def clearBit(self,int_type, offset):
		mask = ~(1 << offset)
		return(int_type & mask)

	# toggleBit() returns an integer with the bit at 'offset' inverted, 0 -> 1 and 1 -> 0.
	def toggleBit(self,int_type, offset):
		mask = 1 << offset
		return(int_type ^ mask)
