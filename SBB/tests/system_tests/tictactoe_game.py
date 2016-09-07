import socket
import select
import json
import sys

class TictactoeGame():
    """
    Implements a TicTacToe match via sockets
    """

    EMPTY = 0
    DRAW = 0

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

    CONFIG = {}

    def __init__(self, test_mode):
        if test_mode:
            TictactoeGame.CONFIG = TictactoeGame.TEST_CONFIG
        else:
            TictactoeGame.CONFIG = TictactoeGame.DEFAULT_CONFIG

        self.valid_requests = ['new_match', 'inputs', 'valid_actions', 
            'perform_action', 'is_over', 'match_result']
        self.player_label = {}
        self._reset_game()
        self._connect_to_sbb()

    def _reset_game(self):
        self.inputs_ = [TictactoeGame.EMPTY, TictactoeGame.EMPTY, TictactoeGame.EMPTY,
                        TictactoeGame.EMPTY, TictactoeGame.EMPTY, TictactoeGame.EMPTY,
                        TictactoeGame.EMPTY, TictactoeGame.EMPTY, TictactoeGame.EMPTY]
        self.result_ = -1

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

    def wait_for_requests(self):
        while True:
            try:
                data = self._get_valid_request()

                message = {
                    'request_result': True,
                    'result': {},
                }

                if TictactoeGame.CONFIG['debug']:
                    print "Request type: "+str(data['request_type'])
            
                if data['request_type'] == 'new_match':
                    self._initialize_match(data)
                elif data['request_type'] == 'inputs':
                    message['result']['inputs'] = self._inputs_from_the_point_of_view_of(data['request_params']['player'])
                elif data['request_type'] == 'valid_actions':
                    message['result']['actions'] = self._valid_actions()
                elif data['request_type'] == 'perform_action':
                    self._perform_action(data['request_params']['player'], data['request_params']['action'])
                elif data['request_type'] == 'is_over':
                    message['result']['is_over'] = self._is_over()
                elif data['request_type'] == 'match_result':
                    message['result']['match_result'] = self._result_for_player(data['request_params']['player'])
                
                self.client_socket.send(json.dumps(message))

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

                if not ('request_type' in data and data['request_type'] in self.valid_requests):
                    raise socket.error("Server did not send a valid request")
        return data

    def _initialize_match(self, data):
        self.player_label[1] = data['request_params']['player1_label']
        self.player_label[2] = data['request_params']['player2_label']
        self._reset_game()

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
    game.wait_for_requests()