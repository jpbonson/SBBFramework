import random
import copy
import numpy
import select
import socket
import json
from collections import defaultdict
from reinforcement_environment import ReinforcementEnvironment, ReinforcementPoint
from default_opponent import DefaultOpponent
from ..config import Config

class DummyOpponent(DefaultOpponent): # TODO
    OPPONENT_ID = "dummy"

    def __init__(self):
        super(DummyOpponent, self).__init__(DummyOpponent.OPPONENT_ID)

    def initialize(self, seed):
        pass

    def execute(self, point_id_, inputs, valid_actions, is_training):
        return 0

class ReinforcementEnvironmentForSockets(ReinforcementEnvironment):
    """
    
    """

    # DONE:
    # - reorganized configs, now it is a .json file
    # - removed clutter / cleaned the code
    # - improved tests (more tests, more organized, and faster)
    # - removed usually-not-useful features (like the bid diversity), to focus on support the relevant parts of the code
    # - generalized sockets code

    # TODO:
    # - testar/melhorar as configs predefinidas
    # - refatorar diversities (para generalizar)
    # - fazer multiplos oponentes funcionarem para sockets
    # - fazer training_opponents_labels ser usado tambem sem o env de sockets?
    # - saber lidar quando nao tiver nenhum oponente
    # - fazer mais tests (system para sockets, e unit tests)
    # - clean code
    # - usar um logger?
    # - melhorar README, com tutorial
    # - melhorar outputs?
    # - conferir run de poker
    # - bug no classification? validation mean muito baixa

    def __init__(self):
        total_actions = Config.USER['reinforcement_parameters']['sockets_parameters']['environment']['actions_total']
        total_inputs = Config.USER['reinforcement_parameters']['sockets_parameters']['environment']['inputs_total']
        total_labels = Config.USER['reinforcement_parameters']['sockets_parameters']['environment']['point_labels_total']
        # t_opponents = []
        # for label in Config.USER['reinforcement_parameters']['sockets_parameters']['environment']['training_opponents_labels']:
        #     t_opponents.append(DummyOpponent(label))
        # coded_opponents_for_training = t_opponents
        # v_opponents = []
        # for label in Config.USER['reinforcement_parameters']['sockets_parameters']['environment']['validation_opponents_labels']:
        #     v_opponents.append(DummyOpponent(label))
        # coded_opponents_for_validation = v_opponents
        coded_opponents_for_training = [DummyOpponent] # TODO
        coded_opponents_for_validation = [DummyOpponent] # TODO
        point_class = ReinforcementPoint
        super(ReinforcementEnvironmentForSockets, self).__init__(total_actions, total_inputs, total_labels, 
            coded_opponents_for_training, coded_opponents_for_validation, point_class)

        self._start_server()

        self.valid_messages = ['match_running', 'match_ended']
        self.valid_params = ['inputs', 'valid_actions', 'result']

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

        self._request(mode, match_id, 'new_match', args = {
            'opponent_label': opponent.opponent_id,
            'point_label': point.label_,
            'seed': point.seed_}
        )

        is_over = False
        while not is_over:
            data = self._get_valid_client_message()

            if data['message_type'] == 'match_running':
                inputs = data['params']['inputs']
                valid_actions = data['params']['valid_actions']
                action = team.execute(point.point_id_, inputs, valid_actions, is_training)
                if action is None:
                    action = random.choice(valid_actions)

                if is_training:
                    team.action_sequence_['coding2'].append(str(action))
                    team.action_sequence_['coding4'].append(str(action))

                self._request(mode, match_id, 'perform_action', args = {'action': action}) 
            elif data['message_type'] == 'match_ended':
                is_over = True
                result = data['params']['result']
                team.action_sequence_['coding3'].append(int(result*2))
            else:
                raise ValueError("Unexpected value for 'message_type'")
        return result

    def _request(self, mode, match_id, message_type, args = {}, response = None):
        if Config.USER['debug']['enabled']:
            print "\nrequest type: "+message_type+", mode: "+str(mode)+", match_id: "+str(match_id)+"\n"
        message = {
            'message_type': message_type,
            'params': {
                'mode': mode, # debug
                'match_id': match_id, # debug
            }
        }
        message['params'].update(args)
        self.connection.send(json.dumps(message))

    def _get_valid_client_message(self):
        try:
            ready = select.select([self.connection], [], [self.connection], 
                Config.USER['reinforcement_parameters']['sockets_parameters']['connection']['timeout'])
            if not ready[0]:
                raise socket.timeout("Timeout to receive messages from client")
            else:
                data = self.connection.recv(Config.USER['reinforcement_parameters']['sockets_parameters']['connection']['buffer'])
                if not data:
                    raise socket.error("Client sent an empty request")
                else:
                    data = json.loads(data)
                    if Config.USER['debug']['enabled']:
                        print "request data: "+str(data)

                    if not 'message_type' in data or not 'params' in data:
                        raise socket.error("Client did not send a valid request, must have the following fields: 'message_type' and 'params'")
                    if data['message_type'] not in self.valid_messages:
                        raise socket.error("Client did not send a valid request, invalid 'message_type'")
                    for item in data['params']:
                        if item not in self.valid_params:
                            raise socket.error("Client did not send a valid request, invalid 'params': "+str(item))
            return data
        except Exception as e:
            print "\n<< It was not possible to connect to the client. >>\n"
            raise e

    def metrics(self):
        msg = ""
        msg += "\n### Environment Info:"
        msg += "\ntotal inputs: "+str(self.total_inputs_)
        msg += "\ntotal actions: "+str(self.total_actions_)
        return msg