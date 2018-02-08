# AliEn token operations handler

import jobs

def main() :
    print "Token.main() says hi"

def init(debug=False, verbose=False) :
    if debug : print "init inside"
    output = jobs.exec_alien_cmd('alien-token-init',verbose)

    if output['returncode'] == 0 :
        print "Token succesfully initialized!"
    else :
        print "Token NOT initialized!"
        if verbose :
            print output['output'].strip()

def info(debug=False, verbose=False) :
    if debug : print "token.info()"
    output = jobs.exec_alien_cmd('alien-token-info',verbose)
    print output['output'].strip()

def destroy(debug=False,verbose=False) :
    if debug : print "destroy inside"
    output = jobs.exec_alien_cmd('alien-token-destroy',verbose)

    if output['returncode'] == 0 :
        print "Token succesfully destroyed!"
    else :
        print "Token not destoyed"
        if verbose :
            print output['output'].strip()

def check(debug=False,verbose=False) :
    token = jobs.exec_alien_cmd('alien-token-info',verbose)

    if token['returncode'] == 1 :
        # not succesfull (no token)
        if verbose : print "Token not validated!"
        if debug : print token
        return False
    else :
        # info succesfull but checking token content
        item = token['output']
        item = item.replace(" ","")
        item = item.split("\n")
        # print item

        # checking host
        if item[0].split(":")[1] == "" :
            print item[0].split(":")[1]
            return False

        # checking Password
        if item[4].split(":")[1] == "" :
            print item[4].split(":")[1]
            return False

        # checking Nonce
        if item[5].split(":")[1] == "" :
            print item[5].split(":")[1]
            return False

        # checking SID
        if item[6].split(":")[1] == "" :
            print item[6].split(":")[1]
            return False

    return True
