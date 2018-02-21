def opposite(c):
    if c== '{': return '}'
    if c== '[': return ']'
    if c== '(': return ')'
    return  c

def getsender(s):
    return s[s.rfind(' '):].strip()

def getnode(s):
    return s[:s.find(' ')].strip()

def getinstance(s):
    node = getnode(s)
    if ":" in node:
        return node.split(':')[0].strip()
    else:
        sender = getsender(s)
        if ':' in sender:
            return sender.split(':')[0].strip()
        else:
            return None

def getnodeonly(s):
    nn = getnode(s)
    if ':' in nn:
        return nn.split(':')[1].strip()
    else:
        return nn

def getsenderonly(s):
    nn = getsender(s)
    if ':' in nn:
        return nn.split(':')[1].strip()
    else:
        return nn


def getfulladdress(s):
    g = getinstance(s)
    n = getnodeonly(s)
    return g + ':' + n

def getfullsender(s):
    n = getsender(s)
    if ':' in n: return n
    g = getinstance(s)
    #n = getsenderonly(s)
    return g + ':' + n

def split(s):
   s = s.strip()
   tokens = []
   token = ''
   tokcount = 0
   sep = ''
   isparam = False
   for c in s:
      if c in [' ', '[', '(', '{', '"', "'"] and sep == '':
          if len(token) != 0 and c == ' ':
              if token == '=' or isparam:
                  isparam = not isparam
                  tokens[-1]+= token
              else:
                tokens.append(token)
              token = ''
              sep = ''
              tokcount=0
          elif c!= ' ':
              sep = c
              tokcount+=1
      elif c in [' ', '[', '(', '{'] and c==sep:
          tokcount+=1
          token += c
      elif c in [']', ')', '}', '"'] and c == opposite(sep):
          tokcount-=1
          if tokcount == 0:
              if token == '=' or isparam:
                  isparam = not isparam
                  tokens[-1]+= token
              else:
                  tokens.append( sep + token + c)
              token = ''
              sep = ''
          else:
              token += c
      else:
          token += c
   if token!='': tokens.append(token)
   return tokens

if __name__ == '__main__':
    cmd = 'one to { "name" : "ahmad sadiq", children [ "a", "b", {"name": "c"}] } "Ahmad Sadiq" { "name" : "ahmad sadiq", children [ "a", "b", {"name": "c"}] }'
    cmd2 = 'one two "Ahmasd Sadiq" three "Garba Shehu"'
    cmd3 = "sadhhjf:cp getnodes checksum = 201 otp = ewhjkfewjknfejknfewkj ah"
    cmd4 = 'script send ["var=1", "when node[0]==1 do var=2"]'
    print (split(cmd))
    print (split(cmd2))
    print (split(cmd3))
    print (split(cmd4))
