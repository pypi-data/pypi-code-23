# ROPGenerator - Gadget_finder module 
# Searching for gadgets and chaining them :) !! 

import Expr
import Database
import Analysis
import re
from Gadget import GadgetType

# Help for the search command
CMD_FIND_HELP =    "\n\t-----------------------------------------------"
CMD_FIND_HELP += "\n\tROPGenerator 'find' command\n\t(Find gadgets that execute specific operations)"
CMD_FIND_HELP += "\n\t-----------------------------------------------"
CMD_FIND_HELP += "\n\n\tUsage:\tfind [OPTIONS] <reg>=<expr>\n\t\tfind [OPTIONS] <reg>=mem(<expr>)\n\t\tfind [OPTIONS] mem(<expr>)=<expr>"
CMD_FIND_HELP += "\n\n\tOptions: No options available for the moment"
CMD_FIND_HELP += "\n\n\tExamples:\n\t\tfind rax=rbp\t\t\t(put the value of rbp in rax)\n\t\tfind rbx=0xff\t\t\t(put the value 255 in rbx)\n\t\tfind rax = mem(rsp)\t\t(pop the top of the stack into rax)\n\t\tfind mem(rsp-8)=rcx\t\t(push rcx onto the stack)\n\t\tfind mem(rbp-0x10)=0b101\t(write 5 at address rbp-16)"


def print_help():
	print(CMD_FIND_HELP)

# The different options
RAW_OUTPUT = True # Output the gadgets addresses raw 
PYTHON_OUTPUT = False # Output the gadgets in python ( like p += <gadget hex>  # commentary )


##############################
# SEARCH ENGINE FOR GADGETS #
############################

class search_engine:

	def __init__(self):
		self.truc = None
	
	def basic_strategy(self, gtype, arg1, arg2, n=1):
		"""
		Search for gadgets basic method ( without chaining ) 
		Returns a list of possible gadgets of maximum size n
		if gtype = GadgetType.REGtoREG, arg1 and arg2 are two ints (register numbers in the IR)
		"""
		if( gtype == GadgetType.REGtoREG ):
			return self._REGtoREG_basic_strategy(arg1, arg2, n=n)
		elif( gtype == GadgetType.CSTtoREG ):
			return self._CSTtoREG_basic_strategy(arg1, arg2, n=n)
		elif( gtype == GadgetType.MEMtoREG ):
			return self._MEMtoREG_basic_strategy(arg1, arg2, n=n)
		elif( gtype == GadgetType.REGtoMEM ):
			return self._REGtoMEM_basic_strategy(arg1, arg2, n=n)
		elif( gtype == GadgetType.CSTtoMEM ):
			return self._CSTtoMEM_basic_strategy(arg1, arg2, n=n)
		elif( gtype == GadgetType.EXPRtoREG ):
			return self._EXPRtoREG_basic_strategy(arg1, arg2, n=n)
		else:
			return []
	
	def _CSTtoREG_basic_strategy(self, reg, cst, n=1):
		"""
		Searches for a gadget that puts directly the constant cst into register reg 
		"""
		db = Database.gadgetLookUp[GadgetType.CSTtoREG]
		if( not cst in db[reg] ):
			return []
		res = []
		for gadget_num in db[reg][cst]:
			if( n <= 0 ):
				break
			else:
				res.append(gadget_num)
		return res
		
	def _CSTtoREG_pop_from_stack_strategy(self, reg, cst, n=1):
		"""
		Returns a payload that puts cst into reg by poping it from the stack 
		"""
		return []
	
	
	def _REGtoREG_basic_strategy(self, reg1, reg2, n=1):
		"""
		Searches for a gadget that puts reg2 into reg1
		reg1, reg2 - int 
		"""
		db = Database.gadgetLookUp[GadgetType.REGtoREG]
		if( not reg2 in db[reg1]):
			return []
		res = []
		for gadget_num in db[reg1][reg2]:
			if( n <= 0 ):
				break
			else:
				n = n - 1
			res.append( gadget_num)
		return res
		
	def _MEMtoREG_basic_strategy(self, reg, addr, n=1):
		"""
		Searches for a gadget that puts mem(addr) into reg
		reg - int, number of the register to affect
		addr - int, number of the register used as an address 
		"""
		db = Database.gadgetLookUp[GadgetType.MEMtoREG]
		if( not addr in db[reg] ):
			return []
		res = []
		for gadget_num in db[reg][addr]:
			if( n <= 0 ):
				break
			else:
				n = n - 1
			res.append( gadget_num )
		return res
	
	def _EXPRtoREG_basic_strategy(self, expr, reg, n=1):
		"""
		Searches for gadgets that put the expression 'expr' into register reg 
		expr - Expr
		reg - int
		"""
		db = Database.gadgetLookUp[GadgetType.EXPRtoREG]
		if( not reg in db ):
			return []
		return db[reg].lookUpEXPRtoREG(expr, n)
		
		
	def _CSTtoMEM_basic_strategy(self, addr_expr, cst, n=1):
		"""
		Searches for gadgets that write the constant cst att mem(addr_expr)
		addr_expr - Expr
		cst - int 
		"""	
		return Database.gadgetLookUp[GadgetType.CSTtoMEM].lookUpCSTtoMEM(addr_expr, cst, n)
	
	def _REGtoMEM_basic_strategy(self, addr_expr, reg, n=1):
		"""
		Searches for gadgets that write reg in the memory at address addr_expr
		addr_expr - Expr
		reg - int, number of the register 
		"""
		return Database.gadgetLookUp[GadgetType.REGtoMEM].lookUpREGtoMEM(addr_expr, reg, n)

# The module-wide search engine 
search = search_engine()

###########################
# COMMAND TO FIND GADGETS #
###########################
	
def find_gadgets(args):
	"""
	Main function to find gadgets !! 
	args - List of user arguments as strings ( command 'find' should not be included in the list as args[0] )
	"""
	
	if( len(Database.gadgetDB) == 0 ):
		print("You have to load gadgets before running the 'find' command (type 'load help' for more details)")
		return 	
	parsed_args = parse_args(args)
	# If parsing returned an error, print it and return 
	if( not parsed_args[0] ):
		print(parsed_args[1])
		return
	# Else execute the search ;) 
	else:
		gtype = parsed_args[1]
		left = parsed_args[2]
		right = parsed_args[3]
		# Search with basic strategy
		gadgets = search.basic_strategy(gtype, left, right, n=10)
		show_gadgets(gadgets)
		
def show_gadgets( gadget_list ):
	"""
	gadget_list is a list of gadget numbers 
	"""
	if( gadget_list ):
		print("\n\tFound matching gadget(s):\n")
	else:
		print("\n\tNo matching gadgets found")
		return 
	if( RAW_OUTPUT ):
		for gadget_num in gadget_list:
			print("\t"+Database.gadgetDB[gadget_num].addrStr + " (" + Database.gadgetDB[gadget_num].asmStr + ")") 
	elif( PYTHON_OUTPUT ):
		print("\t\tPython output not supported yet :'(")
		
	
	
		
def parse_args(args):
	"""
	Parse the user supplied arguments to the 'find' function
	Returns either a tuple (True, GadgetType, x, y )where x and y are:
		if REGtoREG, x and y are register uid for ROPG IR
		if CSTtoREG, x is register uid for ROPG IR and y is an int 
	Or if not supported or invalid arguments, returnsa tuple (False, msg)
	"""
	seen = False
	i = 0 # Argument counter 
	while( i < len(args)):
		arg = args[i]
		# Look for options
		if( arg[0] == '-' ):
			# Ignore
			pass
		# If not option it should be a request expr=expr
		else:	
			if( seen ):
				return (False, "Error. Extra expressions not supported (" + arg + "). Only one at a time please")
			else:
				seen = True
				parsed_expr = parse_user_request(arg)
				if( not parsed_expr[0]):	
					# Maybe the user added millions of spaces, BAD but we try to correct his request syntaxe :/ 
					parsed_expr = parse_user_request(''.join(args[i:]))
					i = len(args)
				if( parsed_expr[0] == False ):
					return (False, parsed_expr[1])
		i = i + 1
	if( not seen ):
		return (False, "Error. Missing specification of gadget to find")
	else:
		return parsed_expr
		
				 
def parse_user_request(req):
	"""
	Parses a user request for a gadget
	Request is of the form  expression=expression
	Returns either a tuple (True, GadgetType, x, y )where x and y are:
		if REGtoREG, x and y are register uid for ROPG IR
		if CSTtoREG, x is register uid for ROPG IR and y is an int 
		
	Or if not supported or invalid arguments, returnsa tuple (False, msg)
	"""

	args = req.split('=')
	if( len(args) != 2):
		return (False, "Invalid request: " + req )
	left = args[0]
	right = args[1]
	# Test if it is XXXtoREG
	if( left in Analysis.regNamesTable):
		# Test if it is REGtoREG
		(success, right_expr) = Expr.parseStrToExpr(right, Analysis.regNamesTable)
		if( not success ):
			return (False, "Error. Operand '"+right+"' is incorrect")
		right_expr = right_expr.simplify()
		if( isinstance(right_expr, Expr.SSAExpr)):
			return (True, GadgetType.REGtoREG, Analysis.regNamesTable[left], right_expr.reg.num)
		# Test if it is MEMtoREG
		elif( isinstance(right_expr, Expr.MEMExpr)):
			splited = right[4:].split(')',1)
			if( len(splited) == 1 or  splited[1] != '' ):
				return ( False, "Error. Operand '"+right+"' is incorrect")
			addr = right_expr.addr
			if( isinstance(addr, Expr.SSAExpr)):
				return (True, GadgetType.MEMtoREG, Analysis.regNamesTable[left], addr.reg.num)
			else:
				return (False, "Error. Memory addresses other than registers are not supported yet") 
		# Test if CSTtoREG
		elif( isinstance(right_expr, Expr.ConstExpr)):
			return ( True, GadgetType.CSTtoREG, Analysis.regNamesTable[left], right_expr.value )
		# Else it is EXPRtoREG
		else:
			return (True, GadgetType.EXPRtoREG, right_expr, Analysis.regNamesTable[left])

	
	elif( left[:4] == 'mem(' ):
		(success,addr) = Expr.parseStrToExpr(left[4:-1], Analysis.regNamesTable)
		if( not success ):
			return (False, "Error. Invalid address: " + left[4:-1] + " ({}".format(addr))
		addr = addr.simplify()
		(success, right_expr) = Expr.parseStrToExpr(right, Analysis.regNamesTable)
		if( not success ):
			return (False, "Error. Invalid operand: " + right + " ({}".format(right_expr))
		right_expr = right_expr.simplify()
		if( isinstance(right_expr, Expr.SSAExpr)):
			return (True, GadgetType.REGtoMEM, addr, right_expr.reg.num)		
		# Test if it is CSTtoMEM
		elif( isinstance( right_expr, Expr.ConstExpr)):
			return ( True, GadgetType.CSTtoMEM, addr, right_expr.value )
		else:
			return (False, "Operand '" +right+"' is invalid or not yet supported by ROPGenerator :(")
	return ( False, "Operand '" +left+"' is invalid or not yet supported by ROPGenerator :(")
	

