import brain.analyzer as analyzer
import interface.command_line as cmd

def main():
    option = 1
    analyzer.revisit_memory()
    while option:
        print "\n1. enter\n2. search\n3. quit\n"
        option = int(raw_input("select - "))
        if option == 1:
            cmd.accept_text()
        elif option == 2:
            cmd.return_text()
        else:
            option = False
    analyzer.remember_for_long_term()
