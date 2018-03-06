import random
import os

def main():
    print("========================================================================\n")
    print("***** RULES OF GAME *****\n")
    print("========================================================================\n")
    print("1] You have 21 sticks , you can take between 1-4 number of sticks, then computer will do same\n")
    print("2] whoever is going to take last stick will be looose game\n")
    print("========================================================================\n")
    print("*** CREATED BY Ganesh Hubale, ganeshhubale03@gmail.com ***\n")
    print("===========================Let's Play===================================\n")

    flag = True
    while True:

            if flag :
                sticks = 21
            print("==============================================================\n")    
            print("sticks available: ", sticks)
            print("\n==============================================================\n")
            if sticks == 0:
                print("============================================================\n")
                print("Match Draw---Sticks are not available\n")
                print("============================================================\n")
                ch = (input("(:: Do you want to play again--> y/n ::)- "))
                print("============================================================\n")
                if ch == 'y':
                    flag = True
                    continue
                else:
                    break

            sticks_chosed = int(input("Enter number of sticks you want: "))
            print("================================================================\n")
            if sticks == 1:
                print("============================================================\n")
                print("*******(:::  You lost :::)*******\n")
                print("============================================================\n")
                ch = (input("(:: Do you want to play again--> y/n ::)- "))
                print("============================================================\n")
                if ch == 'y':
                    flag = True
                    continue
                else:
                    break
            elif sticks_chosed == sticks:
                sticks -= sticks_chosed
                if sticks < 0:
                    print("====================================================\n")
                    print("You broke rules, taken more than available sticks..You loose!!!\n")
                    print("====================================================\n")
                    ch = (input("(:: Do you want to play again--> y/n ::)- "))
                    print("====================================================\n")
                    if ch == 'y':
                        flag = True
                        continue
                    else:
                        break
                if sticks == 0:
                    print("You took all available sticks..Match Draw\n")
                    ch = (input("(:: Do you want to play again--> y/n ::)- "))
                    if ch == 'y':
                        flag = True
                        continue
                    else:
                        break

            elif sticks_chosed >= 5 or sticks_chosed <= 0:
                print("============================================================\n")
                print("Invalid input,  please read the rules!!! you can't take more than 4 or less than 1 stick\n")
                print("============================================================\n")
                flag = False
                continue

            sticks -= sticks_chosed
            if sticks == 1:
            
                print("*******(:: you win ::)*******\n")
            
                ch = (input("(:: Do you want to play again--> y/n ::)- "))
            
                if ch == 'y':
                    flag = True
                    continue
                else:
                    break

            else:

                a = int(random.randint(1, 4))
            

                if a <= sticks:
                
                    print("\ncomputer took: ", a)
                
                    sticks -= a
                    flag = False
                    continue
                else:
                    sticks -= a
                    if sticks < 0:
                    
                        print("computer broke rules, taken more than 4 sticks..You won!!!\n")
                    
                        ch = (input("(:: Do you want to play again--> y/n ::)- "))
                    
                        if ch == 'y':
                            flag = True
                            continue
                        else:
                            break

