from pypokerengine.players import BasePokerPlayer
import random

from pypokerengine.engine.card import Card
from pypokerengine.engine.deck import Deck
from pypokerengine.engine.hand_evaluator import HandEvaluator


class FishPlayer(BasePokerPlayer):  # Do not forget to make parent class as "BasePokerPlayer"

    #  we define the logic to make an action through this method. (so this method would be the core of your AI)
    def declare_action(self, valid_actions, hole_card, round_state):
        # valid_actions format => [raise_action_info, call_action_info, fold_action_info]
        call_action_info = valid_actions[1]
        action, amount = call_action_info["action"], call_action_info["amount"]
        return action, amount   # action returned here is sent to the poker engine

    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass



    def _pick_unused_card(card_num, used_card):
        used = [card.to_id() for card in used_card]
        unused = [card_id for card_id in range(1, 53) if card_id not in used]
        choiced = random.sample(unused, card_num)
        return [Card.from_id(card_id) for card_id in choiced]

    def _fill_community_card(base_cards, used_card):
        need_num = 5 - len(base_cards)
        return base_cards + _pick_unused_card(need_num, used_card)

    def _montecarlo_simulation(self,nb_player, hole_card, community_card):
        community_card = self._fill_community_card(community_card, used_card=hole_card + community_card)
        unused_cards = self._pick_unused_card((nb_player - 1) * 2, hole_card + community_card)
        opponents_hole = [unused_cards[2 * i:2 * i + 2] for i in range(nb_player - 1)]
        opponents_score = [HandEvaluator.eval_hand(hole, community_card) for hole in opponents_hole]
        my_score = HandEvaluator.eval_hand(hole_card, community_card)
        if my_score >= max(opponents_score):
            return 1
        if my_score == max(opponents_score):
            return 0
        if my_score < max(opponents_score):
            return -1

    def handStrength(self,nb_simulation, nb_player, hole_card, community_card=None):
        if not community_card: community_card = []
        ahead = 0.0
        tied = 0.0
        behind = 0.0
        for _ in range(nb_simulation):
            x = self._montecarlo_simulation(nb_player, hole_card, community_card)
            if(x == 1):
                ahead+=1
            if(x == 0):
                tied+=1
            else:
                behind+=1
        return (ahead + tied/2) / (ahead + tied + behind)

    def handPotential(self,nb_simulation, nb_player, hole_card, community_card=None):
        community_card = self._fill_community_card(community_card, used_card=hole_card + community_card)

        ahead = 0
        tied = 1
        behind = 2
        HP = [ [0 , 0, 0],[ 0 , 0, 0 ],[ 0 , 0, 0 ]]
        HPTotal = [0,0,0]
        index = -1
        for _ in range(100):
            unused_cards = self._pick_unused_card((nb_player - 1) * 2, hole_card + community_card)
            opponents_hole = [unused_cards[2 * i:2 * i + 2] for i in range(nb_player - 1)]
            opponents_score = [HandEvaluator.eval_hand(hole, community_card) for hole in opponents_hole]
            my_score = HandEvaluator.eval_hand(hole_card, community_card)
            if(my_score > opponents_score):
                index = 0
            if(my_score == opponents_score):
                index = 1
            if(my_score < opponents_score):
                index = 2

from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate


hole_card = gen_cards(['H4', 'D7'])
community_card = gen_cards(['D3', 'C5', 'C6'])




