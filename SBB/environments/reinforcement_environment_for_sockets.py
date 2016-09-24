import random
import copy
import numpy
import select
import socket
import json
from collections import defaultdict
from reinforcement_environment import ReinforcementEnvironment, ReinforcementPoint
from ..config import Config

# TODO
from tictactoe.tictactoe_opponents import TictactoeRandomOpponent, TictactoeSmartOpponent

class ReinforcementEnvironmentForSockets(ReinforcementEnvironment):
    """
    
    """

    # DONE:
    # - reorganized configs, now it is a .json file
    # - removed clutter / cleaned the code
    # - improved tests (more tests, more organized, and faster)
    # - removed usually-not-useful features (like the bid diversity), to focus on support the relevant parts of the code

    # TODO:
    # - mover partes que chamam o oponente para o socket client (fornecer oponente dummy para _play_match?)
    # - testar as configs predefinidas
    # - refatorar diversities (para generalizar)
    # - fazer reinforcement para sockets ser generico
    # - fazer oponentes se comunicarem via socket? e quando nao tiver oponentes? 
    #       oponentes eh problema do SBB, ou do client? do client
    # - saber lidar quando nao tiver nenhum oponente
    # - fazer mais tests (system para sockets, e unit tests)
    # - clean code
    # - mandar rodar run longo e ver se produz bons resultados
    # - usar um logger?
    # - melhorar README, com tutorial
    # - melhorar outputs?

    def __init__(self):
        total_actions = Config.USER['reinforcement_parameters']['sockets_parameters']['environment']['actions_total']
        total_inputs = Config.USER['reinforcement_parameters']['sockets_parameters']['environment']['inputs_total']
        total_labels = Config.USER['reinforcement_parameters']['sockets_parameters']['environment']['point_labels_total']
        # Config.USER['reinforcement_parameters']['sockets_parameters']['environment']['training_opponents_total']
        # Config.USER['reinforcement_parameters']['sockets_parameters']['environment']['validation_opponents_total']
        coded_opponents_for_training = [TictactoeRandomOpponent, TictactoeSmartOpponent] # TODO
        coded_opponents_for_validation = [TictactoeRandomOpponent, TictactoeSmartOpponent] # TODO
        point_class = ReinforcementPoint
        super(ReinforcementEnvironmentForSockets, self).__init__(total_actions, total_inputs, total_labels, 
            coded_opponents_for_training, coded_opponents_for_validation, point_class)

        self.total_positions_ = 2 # TODO

        self._start_server()

    def _start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((Config.USER['reinforcement_parameters']['sockets_parameters']['connection']['host'], 
            Config.USER['reinforcement_parameters']['sockets_parameters']['connection']['port']))
        self.server_socket.listen(1)
        print "\nWaiting for client socket connection...\n"
        self.connection, self.address = self.server_socket.accept()
        message = {
            'connection': True,
        }
        self.connection.send(json.dumps(message))
        print "\nConnection established.\n"

    def _play_match(self, team, opponent, point, mode, match_id):
        """
        
        """
        
        if mode == Config.RESTRICTIONS['mode']['training']:
            is_training = True
        else:
            is_training = False
        outputs = []
        for position in range(1, self.total_positions_+1):
            if position == 1:
                first_player = opponent
                is_training_for_first_player = False
                second_player = team
                is_training_for_second_player = is_training
                sbb_player = 2
            else:
                first_player = team
                is_training_for_first_player = is_training
                second_player = opponent
                is_training_for_second_player = False
                sbb_player = 1

            args = {'player1_label': first_player.__repr__(), 'player2_label': second_player.__repr__()}
            self._request(mode, match_id, 'new_match', args = args)

            opponent.initialize(point.seed_)
            while True:
                player = 1

                inputs = self._request(mode, match_id, 'inputs', 
                    args = {'player': player}, response = 'inputs')

                valid_actions = self._request(mode, match_id, 'valid_actions', response = 'actions')

                action = first_player.execute(point.point_id_, inputs, valid_actions, 
                    is_training_for_first_player)
                if action is None:
                    action = random.choice(valid_actions)

                if is_training_for_first_player:
                    first_player.action_sequence_['coding2'].append(str(action))
                    first_player.action_sequence_['coding4'].append(str(action))

                self._request(mode, match_id, 'perform_action', args = {'player': player, 'action': action})

                if self._request(mode, match_id, 'is_over', response = 'is_over'):
                    result = self._request(mode, match_id, 'match_result', 
                        args = {'player': sbb_player}, response = 'match_result')
                    outputs.append(result)
                    team.action_sequence_['coding3'].append(int(result*2))
                    break
                player = 2

                inputs = self._request(mode, match_id, 'inputs', 
                    args = {'player': player}, response = 'inputs')

                valid_actions = self._request(mode, match_id, 'valid_actions', response = 'actions')

                action = second_player.execute(point.point_id_, inputs, valid_actions, 
                    is_training_for_second_player)
                if action is None:
                    action = random.choice(valid_actions)
                if is_training_for_second_player:
                    second_player.action_sequence_['coding2'].append(str(action))
                    second_player.action_sequence_['coding4'].append(str(action))

                self._request(mode, match_id, 'perform_action', args = {'player': player, 'action': action})

                if self._request(mode, match_id, 'is_over', response = 'is_over'):
                    result = self._request(mode, match_id, 'match_result', 
                        args = {'player': sbb_player}, response = 'match_result')
                    outputs.append(result)
                    team.action_sequence_['coding3'].append(int(result*2))
                    break

        return numpy.mean(outputs)

    def _request(self, mode, match_id, request_type, args = {}, response = None):
        if Config.USER['debug']['enabled']:
            print "\nrequest type: "+request_type+", mode: "+str(mode)+", match_id: "+str(match_id)+"\n"
        message = {
            'request_type': request_type,
            'request_params': {
                'mode': mode, # internal use + debug
                'match_id': match_id, # debug
            }
        }

        message['request_params'].update(args)

        self.connection.send(json.dumps(message))

        result = []
        try:
            ready = select.select([self.connection], [], [self.connection], 
                Config.USER['reinforcement_parameters']['sockets_parameters']['connection']['timeout'])
            if ready[0]:
                data = self.connection.recv(Config.USER['reinforcement_parameters']['sockets_parameters']['connection']['buffer'])
                if Config.USER['debug']['enabled']:
                    print "data: "+str(data)
                data = json.loads(data)
                if 'request_result' in data and data['request_result']:
                    if Config.USER['debug']['enabled']:
                        print "Request accepted."
                    if response:
                        result = data['result'][response]
                else:
                    raise socket.error("Client did not answer with a valid message")
            else:
                raise socket.timeout("Timeout to receive results of requests messages")
        except Exception as e:
            print "\n<< It was not possible to connect to the SBB client. >>\n"
            raise e

        if Config.USER['debug']['enabled']:
            print "\n"+request_type+" done.\n"

        return result

    def metrics(self):
        msg = ""
        msg += "\n### Environment Info:"
        msg += "\ntotal inputs: "+str(self.total_inputs_)
        msg += "\ntotal actions: "+str(self.total_actions_)
        return msg