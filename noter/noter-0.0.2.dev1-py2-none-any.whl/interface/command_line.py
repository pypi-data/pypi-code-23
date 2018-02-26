import noter.brain.analyzer as analyzer

def accept_text():
    while True:
        text = raw_input("Enter key = ")
        if text == "quit":
            break
        value = analyzer.indexer.get(text, False)
        if value:
            append_value = raw_input("")
            value = "%s. %s" %(value, append_value)
        else:
            print "type to create index"
            value = raw_input("")
        analyzer.indexer.update({text: value})
    return True

def return_text():
    text = raw_input("Enter key = ")
    if text == "quit":
        return True
    value = analyzer.indexer.get(text, False)
    if value:
        print value
    else:
        print "Key does not exists."
    return True

def spit_out():
    for key, value in analyzer.indexer.iteritems():
        print "Key :: %s" %(key)
        print "\n Value is :: "
        print value
        print "\n END OF VALUE FOR %s\n\n" %(key)
    return True


if __name__ == "__main__":
    option = 1
    analyzer.revisit_memory()
    while option:
        print "\n1. enter\n2. search\n3. display all \n4. quit\n"
        option = int(raw_input("select - "))
        if option == 1:
            accept_text()
        elif option == 2:
            return_text()
        elif option == 3:
            spit_out()
        else:
            option = False
    analyzer.remember_for_long_term()

