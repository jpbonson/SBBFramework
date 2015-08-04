import random
from poker_config import PokerConfig
from tables.strenght_table_for_2cards import STRENGTH_TABLE_FOR_2_CARDS
from ..reinforcement_environment import ReinforcementPoint

class PokerPoint(ReinforcementPoint):
    """
    Encapsulates a poker opponent, seeded hand, and position as a point.
    """

    def __init__(self):
        super(PokerPoint, self).__init__()
        self.position_ = random.randint(0, PokerConfig.CONFIG['positions']-1)
        self.sbb_hole_cards = None
        self.opponent_hole_cards = None
        self.sbb_equity_ = None
        self.opponent_equity_ = None
        self.teams_results_ = []
        self.label_ = 0 # TODO: temp

    # def initialize_metrics(self):
    #     sbb_port = PokerConfig.CONFIG['available_ports'][0]
    #     opponent_port = PokerConfig.CONFIG['available_ports'][1]
    #     player1 = 'sbb'
    #     player2 = 'opponent'

    #     t1 = threading.Thread(target=PokerPoint.execute_player, args=[team, opponent, point, sbb_port, is_training, True, True, memories])
    #     t2 = threading.Thread(target=PokerPoint.execute_player, args=[opponent, team, point, opponent_port, False, False, opponent_use_inputs, memories])
    #     args = [PokerConfig.CONFIG['acpc_path']+'dealer', 
    #             PokerConfig.CONFIG['acpc_path']+'outputs/match_output', 
    #             PokerConfig.CONFIG['acpc_path']+'holdem.limit.2p.reverse_blinds.game', 
    #             "1", # total hands 
    #             str(self.seed_),
    #             player1, player2, 
    #             '-p', str(PokerConfig.CONFIG['available_ports'][0])+","+str(PokerConfig.CONFIG['available_ports'][1])]
    #     p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #     t1.start()
    #     t2.start()
    #     out, err = p.communicate()
    #     t1.join()
    #     t2.join()

    def update_metrics(self):
        if self.sbb_hole_cards:
            self.sbb_equity_ = STRENGTH_TABLE_FOR_2_CARDS[frozenset(self.sbb_hole_cards)]
        if self.opponent_hole_cards:
            self.opponent_equity_ = STRENGTH_TABLE_FOR_2_CARDS[frozenset(self.opponent_hole_cards)]

    def __str__(self):
        cards = str(self.sbb_hole_cards)+", "+str(self.opponent_hole_cards)
        metrics = str(self.sbb_equity_)+", "+str(self.opponent_equity_)
        return "(id = ["+str(self.point_id_)+"], attributes = ["+str(self.seed_)+", "+str(self.position_)+"], "+", cards = ["+cards+"], metrics = ["+metrics+"])"

    # @staticmethod
    # def execute_player(player, opponent, point, port, is_training, is_sbb, use_inputs, memories):
    #     if is_sbb and not is_training:
    #         player.extra_metrics_['played_last_hand'] = True

    #     socket_tmp = socket.socket()

    #     total = 10
    #     attempt = 0
    #     while True:
    #         try:
    #             socket_tmp.connect(("localhost", port))
    #             break
    #         except socket_error as e:
    #             attempt += 1
    #             if e.errno == errno.ECONNREFUSED:
    #                 time.sleep(10)
    #             if attempt > total:
    #                 raise ValueError("Could not connect to port "+str(port))

    #     debug_file = None
    #     if Config.USER['reinforcement_parameters']['debug_matches']:
    #         debug_file = open(PokerConfig.CONFIG['acpc_path']+'outputs/player'+str(port)+'.log','w')
    #         print player.__repr__()+": started"
    #     socket_tmp.send("VERSION:2.0.0\r\n")
    #     previous_action = None
    #     partial_messages = []
    #     previous_messages = None
    #     player.initialize(point.seed_) # so a probabilistic opponent will always play equal for the same hands and actions
    #     while True:
    #         try:
    #             message = socket_tmp.recv(1000)
    #         except socket_error as e:
    #             if e.errno == errno.ECONNRESET:
    #                 break
    #             else:
    #                 raise e
    #         if not message:
    #             break
    #         message = message.replace("\r\n", "")
    #         previous_messages = list(partial_messages)
    #         partial_messages = message.split("MATCHSTATE")
    #         last_message = partial_messages[-1] # only cares about the last message sent (ie. the one where this player should act)
    #         match_state = MatchState(last_message, PokerConfig.CONFIG['small_bet'], PokerConfig.CONFIG['big_bet'], PokerConfig.full_deck, PokerConfig.hole_cards_based_on_equity)
    #         if match_state.is_showdown():
    #             previous_action = None
    #             if Config.USER['reinforcement_parameters']['debug_matches']:
    #                 debug_file.write("showdown\n")
    #                 print player.__repr__()+":showdown\n\n"
    #         elif match_state.is_current_player_to_act():
    #             if match_state.is_last_action_a_fold():
    #                 previous_action = None
    #                 if Config.USER['reinforcement_parameters']['debug_matches']:
    #                     debug_file.write("opponent folded\n")
    #                     print player.__repr__()+":opponent folded\n\n"
    #             else:
    #                 if use_inputs:
    #                     chips = PokerConfig.get_chips(player, opponent)
    #                     if len(chips) == 0:
    #                         chips = 0.5
    #                     else:
    #                         chips = PokerConfig.normalize_winning(numpy.mean(chips))
    #                     inputs = match_state.inputs(memories) + [chips] + PokerConfig.get_opponent_model(player, opponent).inputs()
    #                 else:
    #                     inputs = []
    #                 action = player.execute(point.point_id_, inputs, match_state.valid_actions(), is_training)
    #                 if action is None:
    #                     action = 1
    #                 if is_sbb and is_training:
    #                     player.action_sequence_.append(str(action))
    #                 if is_sbb and not is_training:
    #                     if len(match_state.rounds) == 1 and len(match_state.rounds[0]) < 2 and action == 0: # first action of first round is a fold
    #                         player.extra_metrics_['played_last_hand'] = False
    #                 action = PokerConfig.ACTION_MAPPING[action]
    #                 previous_action = action
    #                 send_msg = "MATCHSTATE"+last_message+":"+action+"\r\n"
    #                 try:
    #                     socket_tmp.send(send_msg)
    #                 except socket_error as e:
    #                     if e.errno == errno.ECONNRESET:
    #                         break
    #                 if Config.USER['reinforcement_parameters']['debug_matches']:
    #                     debug_file.write("match_state: "+str(match_state)+"\n\n")
    #                     debug_file.write("inputs: "+str(inputs)+"\n\n")
    #                     debug_file.write("send_msg: "+str(send_msg)+"\n\n")
    #                     print player.__repr__()+":match_state: "+str(match_state)+"\n"
    #                     print player.__repr__()+":inputs: "+str(inputs)+"\n"
    #                     print player.__repr__()+":send_msg: "+str(send_msg)+"\n"
    #         else:
    #             if not previous_action == 'f':
    #                 previous_action = None
    #             if Config.USER['reinforcement_parameters']['debug_matches']:
    #                 debug_file.write("nothing to do\n\n")
    #                 print player.__repr__()+":nothing to do\n"
    #     socket_tmp.close()

    #     if use_inputs:
    #         PokerConfig.update_opponent_model_and_chips(player, opponent, previous_messages+partial_messages, debug_file, previous_action)

    #     updated = False
    #     if is_sbb and not point.sbb_hole_cards:
    #         point.sbb_hole_cards = match_state.current_hole_cards
    #         updated = True
    #     if not is_sbb and not point.opponent_hole_cards:
    #         point.opponent_hole_cards = match_state.current_hole_cards
    #         updated = True
    #     if updated:
    #         point.update_metrics()

    #     if Config.USER['reinforcement_parameters']['debug_matches']:
    #         debug_file.write("The end.\n\n")
    #         print player.__repr__()+": The end.\n"
    #         debug_file.close()