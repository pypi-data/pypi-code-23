#!/bin/python
import roomai.sevenking
import random
random.seed(4)
class HumanInputPlayer(object):
    def receive_info(self, info):
        available_actions = info
    def take_action(self):
        action = input("choosed_acton:")
        #action = ""
        return roomai.sevenking.SevenKingAction.lookup(action)
    def reset(self):
        pass

class HumanInputPlayer1(object):
    def receive_info(self, info):
        available_actions = info
    def take_action(self):
        action = input("choosed_acton:")
        #action = ""
        return roomai.sevenking.SevenKingAction.lookup(action)
    def reset(self):
        pass

def show(info):
    person_state          = info.person_state
    person_state.hand_cards.sort(cmp = roomai.sevenking.SevenKingPokerCard.compare)
    sorted_hand_cards_str = [c.key for c in person_state.hand_cards]
    print ("%s"%(person_state.id) + "'s hand_cards:\t" + ",".join(sorted_hand_cards_str))
    print ("%s"%(person_state.id) + "'s available_actions:\t" + " ".join(person_state.available_actions.keys()))

if __name__ == "__main__":
    players     = [HumanInputPlayer(), HumanInputPlayer1()]
    env         = roomai.sevenking.SevenKingEnv()
    allcards    = roomai.sevenking.AllSevenKingPokerCards.values()[0:17]
    allcards.sort(cmp = roomai.sevenking.SevenKingPokerCard.compare)

    tmp          = allcards[-6]
    allcards[-6] = allcards[-1]
    allcards[-1] = tmp

    tmp          = allcards[-7]
    allcards[-7] = allcards[-2]
    allcards[-2] = tmp


    num_normal_players = len(players)
    infos, public_state, person_states, private_state = env.init({"num_normal_players": num_normal_players,"allcards":allcards})
    for i in range(env.num_normal_players):
        players[i].receive_info(infos[i])
        show(infos[i])
    print (public_state.is_fold)
    print("\n")


    while public_state.is_terminal == False:
        turn = public_state.turn
        print ("turn = %d, stage = %d"%(public_state.turn,public_state.stage))
        action = players[turn].take_action()
        print ("%d player take an action (%s)"%(turn,action.key))
        infos, public_state, person_states, private_state = env.forward(action)
        for i in range(env.num_normal_players):
            players[i].receive_info(infos[i])
            show(infos[i])
        print (public_state.is_fold)
        print ("\n")

    print (public_state.scores)
