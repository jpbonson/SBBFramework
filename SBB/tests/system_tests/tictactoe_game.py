import socket
import select
import json
import sys
import numpy

DEFAULT_CONFIG = {
    'multiply_normalization_by': 10.0,
    'debug': False,
    'timeout': 60,
    'buffer': 5000,
    'port': 7800,
    'host': 'localhost',
    'requests_timeout': 120,
    'silent_errors': False,
}

TEST_CONFIG = {
    'multiply_normalization_by': 10.0,
    'debug': False,
    'timeout': 60,
    'buffer': 5000,
    'port': 7801,
    'host': 'localhost',
    'requests_timeout': 120,
    'silent_errors': True,
}

class TictactoeRandomOpponent():

    def initialize(self, seed):
        self.random_generator_ = numpy.random.RandomState(seed=seed)

    def execute(self, inputs, valid_actions):
        return self.random_generator_.choice(valid_actions)

class TictactoeSmartOpponent():

    def initialize(self, seed):
        self.random_generator_ = numpy.random.RandomState(seed=seed)

    def execute(self, inputs, valid_actions):
        current_player = 1*DEFAULT_CONFIG['multiply_normalization_by']
        opponent_player = 2*DEFAULT_CONFIG['multiply_normalization_by']

        # check if can win in the next move
        for action in valid_actions:
            copy = list(inputs)
            copy[action] = current_player
            winner = self._get_winner_for_inputs(copy)
            if winner == current_player:
                return action

        # check if the opponent could win on their next move, and block them
        for action in valid_actions:
            copy = list(inputs)
            copy[action] = opponent_player
            winner = self._get_winner_for_inputs(copy)
            if winner == opponent_player:
                return action

        # try to take one of the corners
        corners = [0, 2, 6, 8]
        valid_corners = list(set(valid_actions).intersection(corners))
        if valid_corners:
            action = self.random_generator_.choice(valid_corners)
            return action

        # try to take the center
        center = 4
        if center in valid_actions:
            return center

        # get anything that is valid
        action = self.random_generator_.choice(valid_actions)
        return action

    def _get_winner_for_inputs(self, inputs):
        winning_configs = ((0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6),
                       (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6))
        for config in winning_configs:
            if inputs[config[0]] == inputs[config[1]] and inputs[config[1]] == inputs[config[2]]:
                if inputs[config[0]] != 0:
                    return inputs[config[0]]
        return None # no winner

class TictactoeGame():
    """
    Implements a TicTacToe match via sockets
    """

    EMPTY = 0
    DRAW = 0

    CONFIG = {}

    def __init__(self, test_mode):
        if test_mode:
            TictactoeGame.CONFIG = TEST_CONFIG
        else:
            TictactoeGame.CONFIG = DEFAULT_CONFIG

        self.valid_requests = ['new_match', 'perform_action']
        self._connect_to_sbb()

        self.total_positions_ = 2

    def _connect_to_sbb(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.settimeout(TictactoeGame.CONFIG['timeout'])
        try:
            self.client_socket.connect((TictactoeGame.CONFIG['host'], TictactoeGame.CONFIG['port']))
            ready = select.select([self.client_socket], [], [], TictactoeGame.CONFIG['timeout'])
            if not ready[0]:
                raise socket.timeout("Timeout to receive 'success connection' message")
            else:
                data = self.client_socket.recv(TictactoeGame.CONFIG['buffer'])
                data = json.loads(data)
                if 'connection' in data and data['connection']:
                    if TictactoeGame.CONFIG['debug']:
                        print "Connected to SBB server."
                else:
                    raise socket.error("Server did not answer with a 'success connection' message")
                
        except Exception as e:
            if TictactoeGame.CONFIG['silent_errors']:
                raise SystemExit
            else:
                print "\n<< It was not possible to connect to the SBB server. >>\n"
                raise e

    def wait_for_requests(self, message_type = None):
        try:
            data = self._get_valid_request()

            if TictactoeGame.CONFIG['debug']:
                print "Request type: "+str(data['message_type'])

            if message_type and data['message_type'] != message_type:
                raise socket.error("Client was waiting for '"+message_type+"', but received '"+data['message_type']+"'")

            if data['message_type'] == 'new_match':
                self._initialize_match(data)
            elif data['message_type'] == 'perform_action':
                return data['params']['action']
            else:
                raise socket.error("Server did not send a valid request")
            
        except Exception as e:
            if TictactoeGame.CONFIG['silent_errors']:
                raise SystemExit
            else:
                print "\n<< It was not possible to connect to the SBB server. >>\n"
                raise e

    def _get_valid_request(self):
        ready = select.select([self.client_socket], [], [self.client_socket], 
        TictactoeGame.CONFIG['requests_timeout'])
        if not ready[0]:
            raise socket.timeout("Timeout to receive requests messages")
        else:
            data = self.client_socket.recv(TictactoeGame.CONFIG['buffer'])
            if not data:
                raise socket.error("Server sent an empty request")
            else:
                data = json.loads(data)
                if TictactoeGame.CONFIG['debug']:
                    print "request data: "+str(data)

                if not ('message_type' in data and data['message_type'] in self.valid_requests):
                    raise socket.error("Server did not send a valid request")
        return data

    def _initialize_match(self, data):
        self._reset_game()

        current_opponent = data['params']['opponent_id']
        seed = data['params']['seed']
        if current_opponent == 'random': # TODO
            opponent = TictactoeRandomOpponent()
        else:
            opponent = TictactoeSmartOpponent()
        
        outputs = []
        self.player_label = {}
        for position in range(1, self.total_positions_+1):
            if position == 1:
                sbb_player = 2
                self.player_label[1] = 'opponent'
                self.player_label[2] = 'sbb'
            else:
                sbb_player = 1
                self.player_label[1] = 'sbb'
                self.player_label[2] = 'opponent'

            opponent.initialize(seed)
            while True:
                player = 1

                inputs = self._inputs_from_the_point_of_view_of(player)
                valid_actions = self._valid_actions()
                if player == sbb_player:
                    message = {
                        'message_type': 'match_running',
                        'params': {
                            'inputs': inputs,
                            'valid_actions': valid_actions,
                        },
                    }
                    if TictactoeGame.CONFIG['debug']:
                        print "message data: "+str(message)
                    self.client_socket.send(json.dumps(message))
                    action = self.wait_for_requests('perform_action')
                else:
                    action = opponent.execute(inputs, valid_actions)
                self._perform_action(player, action)

                if self._is_over():
                    result = self._result_for_player(sbb_player)
                    outputs.append(result)
                    self._reset_game()
                    break

                player = 2

                inputs = self._inputs_from_the_point_of_view_of(player)
                valid_actions = self._valid_actions()
                if player == sbb_player:
                    message = {
                        'message_type': 'match_running',
                        'params': {
                            'inputs': inputs,
                            'valid_actions': valid_actions,
                        },
                    }
                    if TictactoeGame.CONFIG['debug']:
                        print "message data: "+str(message)
                    self.client_socket.send(json.dumps(message))
                    action = self.wait_for_requests('perform_action')
                else:
                    action = opponent.execute(inputs, valid_actions)
                self._perform_action(player, action)

                if self._is_over():
                    result = self._result_for_player(sbb_player)
                    outputs.append(result)
                    self._reset_game()
                    break

        final_result = numpy.mean(outputs)
        message = {
            'message_type': 'match_ended',
            'params': {
                'result': final_result,
            },
        }
        if TictactoeGame.CONFIG['debug']:
            print "message data: "+str(message)
        self.client_socket.send(json.dumps(message))

    def _reset_game(self):
        self.inputs_ = [TictactoeGame.EMPTY, TictactoeGame.EMPTY, TictactoeGame.EMPTY,
                        TictactoeGame.EMPTY, TictactoeGame.EMPTY, TictactoeGame.EMPTY,
                        TictactoeGame.EMPTY, TictactoeGame.EMPTY, TictactoeGame.EMPTY]
        self.result_ = -1

    def _inputs_from_the_point_of_view_of(self, position):
        """
        Get a copy of the inputs so that the player in 'position' always see the board with 
        spaces with '1' as their spaces, and '2' as the opponent's spaces.
        """
        if position == 1:
            return [x*TictactoeGame.CONFIG['multiply_normalization_by'] for x in list(self.inputs_)]
        else:
            mapping = [0, 2, 1]
            inputs = [mapping[x]*TictactoeGame.CONFIG['multiply_normalization_by'] for x in list(self.inputs_)]
            return inputs

    def _valid_actions(self):
        """
        The valid actions are the empty spaces.
        """
        valids = []
        for index, space in enumerate(self.inputs_):
            if space == TictactoeGame.EMPTY:
                valids.append(index)
        return valids

    def _perform_action(self, current_player, action):
        """
        Perform the action for the current_player in the board, modifying 
        the attribute inputs_.
        """
        self.inputs_[action] = current_player
        if TictactoeGame.CONFIG['debug']:
            print "---"
            print str(self.inputs_[0:3])
            print str(self.inputs_[3:6])
            print str(self.inputs_[6:9])

    def _is_over(self):
        """
        Check if all spaces were used. If yes, sets the attribute result_ with the 
        number of the winner or 0 if a draw occured.
        """
        winner = self._get_winner()
        if winner:
            self.result_ = winner
            if TictactoeGame.CONFIG['debug']:
                print "It is over! Player "+str(self.result_)+" ("+str(self.player_label[self.result_])+") wins!"
            return True
        for value in self.inputs_:
            if value == TictactoeGame.EMPTY:
                if TictactoeGame.CONFIG['debug']:
                    print "Go!"
                return False
        self.result_ = TictactoeGame.DRAW
        if TictactoeGame.CONFIG['debug']:
            print "It is over! Draw!"
        return True

    def _get_winner(self):
        winning_configs = ((0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6),
                       (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6))
        for config in winning_configs:
            if (self.inputs_[config[0]] == self.inputs_[config[1]] 
                and self.inputs_[config[1]] == self.inputs_[config[2]]
                and self.inputs_[config[0]] != 0):
                return self.inputs_[config[0]]
        return None # no winner

    def _result_for_player(self, current_player):
        if self.result_ == current_player:
            return 1 # win
        if self.result_ == TictactoeGame.DRAW:
            return 0.5 # draw
        else:
            return 0 # lose

if __name__ == "__main__":
    test_mode = False
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_mode = True
    game = TictactoeGame(test_mode)
    while True:
        game.wait_for_requests()