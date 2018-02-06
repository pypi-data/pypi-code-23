from coda.parser import Parser
p = Parser()
s = p.parse_file(open('../test2.txt'))
for st in s:
    print (st.acc_number)
    print (st.currency)