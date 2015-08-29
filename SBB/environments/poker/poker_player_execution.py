import errno
import socket
import time
from socket import error as socket_error
import numpy
from opponent_model import OpponentModel
from match_state import MatchState
from poker_config import PokerConfig
from ...config import Config

class PokerPlayerExecution():
    """

    """

    @staticmethod
    def execute_player(player, opponent, point, port, is_training, is_sbb, inputs_type):
        if is_sbb and not is_training:
            player.extra_metrics_['played_last_hand'] = True

        socket_tmp = socket.socket()

        total = 100
        attempt = 0
        while True:
            try:
                socket_tmp.connect(("localhost", port))
                break
            except socket_error as e:
                attempt += 1
                if e.errno == errno.ECONNREFUSED:
                    time.sleep(1)
                if attempt > total:
                    raise ValueError("Could not connect to port "+str(port))

        debug_file = None
        if Config.USER['reinforcement_parameters']['debug_matches']:
            debug_file = open(PokerConfig.CONFIG['acpc_path']+'outputs/player'+str(port)+'.log','w')
            print player.__repr__()+": started"
        socket_tmp.send("VERSION:2.0.0\r\n")
        previous_action = None
        partial_messages = []
        previous_messages = None
        player.initialize(point.seed_) # so a probabilistic opponent will always play equal for the same hands and actions
        while True:
            try:
                message = socket_tmp.recv(1000)
            except socket_error as e:
                if e.errno == errno.ECONNRESET:
                    break
                else:
                    raise e
            if not message:
                break
            message = message.replace("\r\n", "")
            previous_messages = list(partial_messages)
            partial_messages = message.split("MATCHSTATE")
            last_message = partial_messages[-1] # only cares about the last message sent (ie. the one where this player should act)
            match_state = MatchState(last_message, PokerConfig.CONFIG['small_bet'], PokerConfig.CONFIG['big_bet'])
            if match_state.is_showdown():
                previous_action = None
                if Config.USER['reinforcement_parameters']['debug_matches']:
                    debug_file.write("showdown\n")
                    print player.__repr__()+":showdown\n\n"
            elif match_state.is_current_player_to_act():
                if match_state.is_last_action_a_fold():
                    previous_action = None
                    if Config.USER['reinforcement_parameters']['debug_matches']:
                        debug_file.write("opponent folded\n")
                        print player.__repr__()+":opponent folded\n\n"
                else:
                    if inputs_type:
                        if inputs_type == 'all':
                            if is_sbb:
                                point_inputs = point.inputs(len(match_state.rounds))
                            else:
                                point_inputs = point.inputs_for_opponent(len(match_state.rounds))
                            chips = PokerPlayerExecution._calculate_chips_input(player, opponent)
                            inputs = point_inputs + match_state.inputs() + [chips] + PokerPlayerExecution._get_opponent_model(player, opponent).inputs(match_state)
                        elif inputs_type == 'rule_based_opponent':
                            inputs = []
                            inputs.append(point.hand_strength_[len(match_state.rounds)-1])
                            inputs.append(match_state.calculate_bet()*Config.RESTRICTIONS['multiply_normalization_by'])
                    else:
                        inputs = []
                    action = player.execute(point.point_id_, inputs, match_state.valid_actions(), is_training)
                    if action is None:
                        action = 1
                    if is_sbb and is_training:
                        player.action_sequence_.append(str(action))
                    if is_sbb and not is_training:
                        if len(match_state.rounds) == 1 and len(match_state.rounds[0]) < 2 and action == 0: # first action of first round is a fold
                            player.extra_metrics_['played_last_hand'] = False
                    action = PokerConfig.CONFIG['action_mapping'][action]
                    previous_action = action
                    send_msg = "MATCHSTATE"+last_message+":"+action+"\r\n"
                    try:
                        socket_tmp.send(send_msg)
                    except socket_error as e:
                        if e.errno == errno.ECONNRESET:
                            break
                    if Config.USER['reinforcement_parameters']['debug_matches']:
                        debug_file.write("match_state: "+str(match_state)+"\n\n")
                        debug_file.write("inputs: "+str(inputs)+"\n\n")
                        debug_file.write("send_msg: "+str(send_msg)+"\n\n")
                        print player.__repr__()+":match_state: "+str(match_state)+"\n"
                        print player.__repr__()+":inputs: "+str(inputs)+"\n"
                        print player.__repr__()+":send_msg: "+str(send_msg)+"\n"
            else:
                if not previous_action == 'f':
                    previous_action = None
                if Config.USER['reinforcement_parameters']['debug_matches']:
                    debug_file.write("nothing to do\n\n")
                    print player.__repr__()+":nothing to do\n"
        socket_tmp.close()

        if inputs_type and inputs_type == 'all':
            PokerPlayerExecution._update_opponent_model(player, opponent, point, previous_messages+partial_messages, debug_file, previous_action)

        if Config.USER['reinforcement_parameters']['debug_matches']:
            debug_file.write("The end.\n\n")
            print player.__repr__()+": The end.\n"
            debug_file.close()

    @staticmethod
    def _calculate_chips_input(player, opponent):
        chips = PokerPlayerExecution.get_chips(player, opponent)
        if len(chips) == 0:
            chips = 0.5
        else:
            chips = numpy.mean(chips)
        chips = chips*Config.RESTRICTIONS['multiply_normalization_by']
        return chips

    @staticmethod
    def get_chips(player, opponent):
        opponent_id = PokerPlayerExecution._get_opponent_id(opponent)
        if opponent_id not in player.chips:
            player.chips[opponent_id] = []
        return player.chips[opponent_id]

    @staticmethod
    def _get_opponent_model(player, opponent):
        opponent_id = PokerPlayerExecution._get_opponent_id(opponent)
        if opponent_id not in player.opponent_model:
            player.opponent_model[opponent_id] = OpponentModel()
        return player.opponent_model[opponent_id]

    @staticmethod
    def _get_opponent_id(opponent):
        if opponent.opponent_id == "hall_of_fame":
            opponent_id = opponent.team_id_
        else:
            opponent_id = opponent.opponent_id
        return opponent_id

    @staticmethod
    def _update_opponent_model(player, opponent, point, messages, debug_file, previous_action):
        for partial_msg in reversed(messages):
            if partial_msg:
                partial_match_state = MatchState(partial_msg, PokerConfig.CONFIG['small_bet'], PokerConfig.CONFIG['big_bet'])
                self_actions, opponent_actions = partial_match_state.actions_per_player()
                if partial_match_state.is_showdown():
                    if Config.USER['reinforcement_parameters']['debug_matches']:
                        debug_file.write("partial_msg: "+str(partial_msg)+", showdown\n\n")
                        print player.__repr__()+": partial_msg: "+str(partial_msg)+", showdown\n"
                    self_folded = False
                    opponent_folded = False
                else:
                    last_player = partial_match_state.last_player_to_act()
                    if last_player == partial_match_state.position:
                        if self_actions and self_actions[-1] == 'f':
                            if Config.USER['reinforcement_parameters']['debug_matches']:
                                debug_file.write("partial_msg: "+str(partial_msg)+", I folded\n\n")
                                print player.__repr__()+": partial_msg: "+str(partial_msg)+", I folded\n"
                            self_folded = True
                            opponent_folded = False
                    elif opponent_actions and opponent_actions[-1] == 'f':
                        if Config.USER['reinforcement_parameters']['debug_matches']:
                            debug_file.write("partial_msg: "+str(partial_msg)+", opponent folded\n\n")
                            print player.__repr__()+": partial_msg: "+str(partial_msg)+", opponent folded\n"
                        self_folded = False
                        opponent_folded = True
                    else:
                        raise ValueError("An unexpected behavior occured during the poker match!")
                PokerPlayerExecution._get_opponent_model(player, opponent).update_overall_agressiveness(len(partial_match_state.rounds), self_actions, opponent_actions, self_folded, opponent_folded, previous_action)
                break