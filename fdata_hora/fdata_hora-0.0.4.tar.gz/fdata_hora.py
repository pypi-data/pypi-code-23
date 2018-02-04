import os, sys
import time
import datetime
from datetime import datetime 
import shlex
import locale
class Fdata_hora():


	def geraTimeStamp(self):
		datahora = datetime.now()
		#tag_hora = "%s-%s-%s_%s%s"%(datahora.day, datahora.month, datahora.year, datahora.hour, datahora.minute)
		datahora = datahora.strftime("%d%b%Y-%H_%Mhs%Ss")
		#return tag_hora
		return datahora

	def getDMY(self,vartempo):
		if vartempo == "dia":
			dia = str(datetime.now().strftime("%d"))
			return dia
		elif vartempo == "nomedia":
			dianome = str(datetime.now().strftime("%a"))
			return dianome
		elif vartempo == "mes":
			mes =  str(datetime.now().strftime("%m"))
			return mes
		elif vartempo == "nomemes":
			nomemes =  str(datetime.now().strftime("%b"))
			return nomemes
		elif vartempo == "ano":
			ano = str(datetime.now().strftime("%Y"))
			return ano

getdata = Data_Hora()
