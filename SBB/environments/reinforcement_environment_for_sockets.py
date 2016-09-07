import random
import copy
import numpy
import select
import socket
import json
from collections import defaultdict
from default_environment import DefaultEnvironment, DefaultPoint, reset_points_ids
from reinforcement_environment import ReinforcementEnvironment, ReinforcementPoint
from ..core.team import Team
from ..core.diversity_maintenance import DiversityMaintenance
from ..core.pareto_dominance_for_points import ParetoDominanceForPoints
from ..core.pareto_dominance_for_teams import ParetoDominanceForTeams
from ..utils.helpers import round_value, flatten, accumulative_performances, rank_teams_by_accumulative_score
from ..config import Config

# AQUI
from tictactoe.tictactoe_opponents import TictactoeRandomOpponent, TictactoeSmartOpponent

class ReinforcementEnvironmentForSockets(ReinforcementEnvironment):
    """
    
    """

    # TODO:
    # - implementar tictactoe_game com tictactoe_environment para sockets
    # - limpar codigo de requests
    # - fazer arquivo externo para config
    # - atualizar testes para usar setUp e tearDown
    # - fazer reinforcement para sockets ser generico
    # - fazer oponentes se comunicarem via socket

    def __init__(self):
        total_actions = 9 # spaces in the board
        total_inputs = 9 # spaces in the board (0, 1, 2 as the states, 0: no player, 1: player 1, 2: player 2)
        total_labels = 1 # since no labels are being used, group everything is just one label
        coded_opponents_for_training = [TictactoeRandomOpponent, TictactoeSmartOpponent]
        coded_opponents_for_validation = [TictactoeRandomOpponent, TictactoeSmartOpponent]
        point_class = ReinforcementPoint
        super(ReinforcementEnvironmentForSockets, self).__init__(total_actions, total_inputs, total_labels, coded_opponents_for_training, coded_opponents_for_validation, point_class)
        
        self.total_positions_ = 2
        self.action_mapping_ = {
            '[0,0]': 0, '[0,1]': 1, '[0,2]': 2,
            '[1,0]': 3, '[1,1]': 4, '[1,2]': 5,
            '[2,0]': 6, '[2,1]': 7, '[2,2]': 8,
        }
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((Config.USER['advanced_training_parameters']['sockets_parameters']['host'], Config.USER['advanced_training_parameters']['sockets_parameters']['port'])) # TODO: porta configuravel (porta diferente para tests)
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

            self._request_match(team, opponent, point, mode, match_id, 
                player1_label = first_player.__repr__(), player2_label = second_player.__repr__())

            opponent.initialize(point.seed_)
            while True:
                player = 1

                inputs = self._request_inputs_from_the_point_of_view_of(player, mode, match_id)

                valid_actions = self._request_valid_actions(mode, match_id)

                action = first_player.execute(point.point_id_, inputs, valid_actions, is_training_for_first_player)
                if action is None:
                    action = random.choice(valid_actions)

                if is_training_for_first_player:
                    first_player.action_sequence_['coding2'].append(str(action))
                    first_player.action_sequence_['coding4'].append(str(action))

                self._request_perform_action(player, action, mode, match_id)

                if self._request_is_over(mode, match_id):
                    result = self._request_result_for_player(sbb_player, mode, match_id)
                    outputs.append(result)
                    team.action_sequence_['coding3'].append(int(result*2))
                    break
                player = 2

                inputs = self._request_inputs_from_the_point_of_view_of(player, mode, match_id)

                valid_actions = self._request_valid_actions(mode, match_id)

                action = second_player.execute(point.point_id_, inputs, valid_actions, is_training_for_second_player)
                if action is None:
                    action = random.choice(valid_actions)
                if is_training_for_second_player:
                    second_player.action_sequence_['coding2'].append(str(action))
                    second_player.action_sequence_['coding4'].append(str(action))

                self._request_perform_action(player, action, mode, match_id)

                if self._request_is_over(mode, match_id):
                    result = self._request_result_for_player(sbb_player, mode, match_id)
                    outputs.append(result)
                    team.action_sequence_['coding3'].append(int(result*2))
                    break
        return numpy.mean(outputs)

    def _request_match(self, team, opponent, point, mode, match_id, player1_label, player2_label):
        if Config.USER['advanced_training_parameters']['sockets_parameters']['debug']:
            print "\nAsking for a new match... match_id: "+str(match_id)+"\n"
        message = {
            'request_type': 'new_match',
            'request_params': {
                'mode': mode, # internal use + debug
                'match_id': match_id, # debug
                'player1_label': player1_label,
                'player2_label': player2_label,
            }
        }
        self.connection.send(json.dumps(message))

        try:
            ready = select.select([self.connection], [], [self.connection], Config.USER['advanced_training_parameters']['sockets_parameters']['requests_timeout'])
            if ready[0]:
                data = self.connection.recv(Config.USER['advanced_training_parameters']['sockets_parameters']['buffer'])
                if Config.USER['advanced_training_parameters']['sockets_parameters']['debug']:
                    print "data: "+str(data)
                data = json.loads(data)
                if 'request_result' in data and data['request_result']:
                    if Config.USER['advanced_training_parameters']['sockets_parameters']['debug']:
                        print "Request accepted."
                else:
                    raise socket.error("Client did not answer with a valid message")
            else:
                raise socket.timeout("Timeout to receive results of requests messages")
        except Exception as e:
            print "\n<< It was not possible to connect to the SBB client. >>\n"
            raise e

        if Config.USER['advanced_training_parameters']['sockets_parameters']['debug']:
            print "\nNew match ready.\n"

    def _request_inputs_from_the_point_of_view_of(self, player, mode, match_id):
        if Config.USER['advanced_training_parameters']['sockets_parameters']['debug']:
            print "\nAsking for inputs for player "+str(player)+"... match_id: "+str(match_id)+"\n"
        message = {
            'request_type': 'inputs',
            'request_params': {
                'mode': mode, # internal use + debug
                'match_id': match_id, # debug
                'player': player,
            }
        }
        self.connection.send(json.dumps(message))

        result = []
        try:
            ready = select.select([self.connection], [], [self.connection], Config.USER['advanced_training_parameters']['sockets_parameters']['requests_timeout'])
            if ready[0]:
                data = self.connection.recv(Config.USER['advanced_training_parameters']['sockets_parameters']['buffer'])
                if Config.USER['advanced_training_parameters']['sockets_parameters']['debug']:
                    print "data: "+str(data)
                data = json.loads(data)
                if 'request_result' in data and data['request_result']:
                    if Config.USER['advanced_training_parameters']['sockets_parameters']['debug']:
                        print "Request accepted."
                    result = data['result']['inputs']
                else:
                    raise socket.error("Client did not answer with a valid message")
            else:
                raise socket.timeout("Timeout to receive results of requests messages")
        except Exception as e:
            print "\n<< It was not possible to connect to the SBB client. >>\n"
            raise e

        if Config.USER['advanced_training_parameters']['sockets_parameters']['debug']:
            print "\nInputs ready.\n"

        return result

    def _request_valid_actions(self, mode, match_id):
        if Config.USER['advanced_training_parameters']['sockets_parameters']['debug']:
            print "\nAsking for valid actions... match_id: "+str(match_id)+"\n"
        message = {
            'request_type': 'valid_actions',
            'request_params': {
                'mode': mode, # internal use + debug
                'match_id': match_id, # debug
            }
        }
        self.connection.send(json.dumps(message))

        result = []
        try:
            ready = select.select([self.connection], [], [self.connection], Config.USER['advanced_training_parameters']['sockets_parameters']['requests_timeout'])
            if ready[0]:
                data = self.connection.recv(Config.USER['advanced_training_parameters']['sockets_parameters']['buffer'])
                if Config.USER['advanced_training_parameters']['sockets_parameters']['debug']:
                    print "data: "+str(data)
                data = json.loads(data)
                if 'request_result' in data and data['request_result']:
                    if Config.USER['advanced_training_parameters']['sockets_parameters']['debug']:
                        print "Request accepted."
                    result = data['result']['actions']
                else:
                    raise socket.error("Client did not answer with a valid message")
            else:
                raise socket.timeout("Timeout to receive results of requests messages")
        except Exception as e:
            print "\n<< It was not possible to connect to the SBB client. >>\n"
            raise e

        if Config.USER['advanced_training_parameters']['sockets_parameters']['debug']:
            print "\nValid actions ready.\n"

        return result

    def _request_perform_action(self, player, action, mode, match_id):
        if Config.USER['advanced_training_parameters']['sockets_parameters']['debug']:
            print "\nAsking for perform action... match_id: "+str(match_id)+"\n"
        message = {
            'request_type': 'perform_action',
            'request_params': {
                'mode': mode, # internal use + debug
                'match_id': match_id, # debug
                'player': player,
                'action': action,
            }
        }
        self.connection.send(json.dumps(message))

        try:
            ready = select.select([self.connection], [], [self.connection], Config.USER['advanced_training_parameters']['sockets_parameters']['requests_timeout'])
            if ready[0]:
                data = self.connection.recv(Config.USER['advanced_training_parameters']['sockets_parameters']['buffer'])
                if Config.USER['advanced_training_parameters']['sockets_parameters']['debug']:
                    print "data: "+str(data)
                data = json.loads(data)
                if 'request_result' in data and data['request_result']:
                    if Config.USER['advanced_training_parameters']['sockets_parameters']['debug']:
                        print "Request accepted."
                else:
                    raise socket.error("Client did not answer with a valid message")
            else:
                raise socket.timeout("Timeout to receive results of requests messages")
        except Exception as e:
            print "\n<< It was not possible to connect to the SBB client. >>\n"
            raise e

        if Config.USER['advanced_training_parameters']['sockets_parameters']['debug']:
            print "\nPerform action ready.\n"

    def _request_is_over(self, mode, match_id):
        if Config.USER['advanced_training_parameters']['sockets_parameters']['debug']:
            print "\nAsking for is_over... match_id: "+str(match_id)+"\n"
        message = {
            'request_type': 'is_over',
            'request_params': {
                'mode': mode, # internal use + debug
                'match_id': match_id, # debug
            }
        }
        self.connection.send(json.dumps(message))

        result = []
        try:
            ready = select.select([self.connection], [], [self.connection], Config.USER['advanced_training_parameters']['sockets_parameters']['requests_timeout'])
            if ready[0]:
                data = self.connection.recv(Config.USER['advanced_training_parameters']['sockets_parameters']['buffer'])
                if Config.USER['advanced_training_parameters']['sockets_parameters']['debug']:
                    print "data: "+str(data)
                data = json.loads(data)
                if 'request_result' in data and data['request_result']:
                    if Config.USER['advanced_training_parameters']['sockets_parameters']['debug']:
                        print "Request accepted."
                    result = data['result']['is_over']
                else:
                    raise socket.error("Client did not answer with a valid message")
            else:
                raise socket.timeout("Timeout to receive results of requests messages")
        except Exception as e:
            print "\n<< It was not possible to connect to the SBB client. >>\n"
            raise e

        if Config.USER['advanced_training_parameters']['sockets_parameters']['debug']:
            print "\nis_over ready.\n"

        return result

    def _request_result_for_player(self, sbb_player, mode, match_id):
        if Config.USER['advanced_training_parameters']['sockets_parameters']['debug']:
            print "\nAsking for is_over... match_id: "+str(match_id)+"\n"
        message = {
            'request_type': 'match_result',
            'request_params': {
                'mode': mode, # internal use + debug
                'match_id': match_id, # debug
                'player': sbb_player,
            }
        }
        self.connection.send(json.dumps(message))

        result = []
        try:
            ready = select.select([self.connection], [], [self.connection], Config.USER['advanced_training_parameters']['sockets_parameters']['requests_timeout'])
            if ready[0]:
                data = self.connection.recv(Config.USER['advanced_training_parameters']['sockets_parameters']['buffer'])
                if Config.USER['advanced_training_parameters']['sockets_parameters']['debug']:
                    print "data: "+str(data)
                data = json.loads(data)
                if 'request_result' in data and data['request_result']:
                    if Config.USER['advanced_training_parameters']['sockets_parameters']['debug']:
                        print "Request accepted."
                    result = data['result']['match_result']
                else:
                    raise socket.error("Client did not answer with a valid message")
            else:
                raise socket.timeout("Timeout to receive results of requests messages")
        except Exception as e:
            print "\n<< It was not possible to connect to the SBB client. >>\n"
            raise e

        if Config.USER['advanced_training_parameters']['sockets_parameters']['debug']:
            print "\nis_over ready.\n"

        return result

    def metrics(self):
        msg = ""
        msg += "\n### Environment Info:"
        msg += "\ntotal inputs: "+str(self.total_inputs_)
        msg += "\ntotal actions: "+str(self.total_actions_)
        msg += "\nactions mapping: "+str(self.action_mapping_)
        msg += "\npositions: "+str(self.total_positions_)
        return msg