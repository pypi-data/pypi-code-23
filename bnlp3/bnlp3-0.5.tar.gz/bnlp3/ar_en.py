#-*- coding: utf-8 -*-
ar_en = {}

#tha, ha, ba, sin, ra, qaf, lam, nun
consonants_ar = ['\u062b', '\u062d', '\u0628', '\u0633','\u0631', '\u0642', '\u0644', '\u0646']

#alif, wa, ya
vowels_ar = ['\u0627','\u0648','\u064a']

#consonants_en = ['b','c','d','f','g','h','

#blank space
ar_en[' '] = ['',' ']

#alif
ar_en['\u0627'] = ['a','o']

#alif hamza
ar_en['\u0623'] = ['a']

#alif hamza with hamza at bottom
ar_en['\u0625'] = ['i']

#ba
ar_en['\u0628'] = ['b']

# ta
ar_en['\u062a'] = ['t']

# tha
ar_en['\u062b'] = ['th']

#ja/ga
ar_en['\u062c'] = ['j','g','ja','ga']

# ha'
ar_en['\u062d'] = ['h','ha','he']

# dal
ar_en['\u062f'] = ['d']

# ghayn
ar_en['\u063a'] = ['gh']

#ra
ar_en['\u0631'] = ['r','ra']

# za
ar_en['\u0632'] = ['z','zz']

#sin
ar_en['\u0633'] = ['s','sa']

#shin connected
ar_en['\u0634'] = ['sh','shu','sha']

#sad
ar_en['\u0635'] = ['s','sa']

#deep ta
ar_en['\u0637'] = ['t','ta']

# ayn
ar_en['\u0639'] = ['3','a','']

# fa
ar_en['\u0641'] = ['f','fa']

#qaf
ar_en['\u0642'] = ['q','qu']

#kaf
ar_en['\u0643'] = ['k','ka']

##lam
ar_en['\u0644'] = ['l','l-','l ','s','s-','s ','sh','sh-','sh ','t','t-','t ','th','th-','th ','la','li']

#mim solo
ar_en['\u0645'] = ['m','ma','mu']

#nun
ar_en['\u0646'] = ['n', 'na']

#tar ma-buta
ar_en['\u0629'] = ['a','at']

#light ha/he
ar_en['\u0647'] = ['','h','ha','he']

#wa
ar_en['\u0648'] = ['u','o','w','wa']

# ya, said ee
ar_en['\u064a'] = ['y','i','iyy','yyi','ee']

#hamza solo
ar_en['\u0621'] = [""]

#hamza on ya
ar_en['\u0626'] = ['i',"'i"]

#left-to-right mark
ar_en['\u200e'] = ['']
