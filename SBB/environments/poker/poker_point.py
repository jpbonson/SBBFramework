import random
import time
import errno
import socket
from socket import error as socket_error
import subprocess
import threading
from match_state import MatchState
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
        self.label_ = 0
        self.sbb_equity_ = None
        self.opponent_equity_ = None
        self.teams_results_ = []
        self._initialize_metrics()

    def _initialize_metrics(self):
        sbb_port = PokerConfig.CONFIG['available_ports'][0]
        opponent_port = PokerConfig.CONFIG['available_ports'][1]
        player1 = 'sbb'
        player2 = 'opponent'

        t1 = threading.Thread(target=PokerPoint.test_execution, args=[self, sbb_port, True])
        t2 = threading.Thread(target=PokerPoint.test_execution, args=[self, opponent_port, False])
        args = [PokerConfig.CONFIG['acpc_path']+'dealer', 
                PokerConfig.CONFIG['acpc_path']+'outputs/match_output', 
                PokerConfig.CONFIG['acpc_path']+'holdem.limit.2p.reverse_blinds.game', 
                "1", # total hands 
                str(self.seed_),
                player1, player2, 
                '-p', str(PokerConfig.CONFIG['available_ports'][0])+","+str(PokerConfig.CONFIG['available_ports'][1]),
                '-l']
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        t1.start()
        t2.start()
        out, err = p.communicate()
        t1.join()
        t2.join()

        self.sbb_equity_ = MatchState.calculate_equity(self.sbb_hole_cards)
        self.opponent_equity_ = MatchState.calculate_equity(self.opponent_hole_cards)
        self.label_ = self._get_label()

    def _get_label(self):
        return 0 # TODO

    def __str__(self):
        cards = str(self.sbb_hole_cards)+", "+str(self.opponent_hole_cards)
        metrics = str(self.sbb_equity_)+", "+str(self.opponent_equity_)
        return "(id = ["+str(self.point_id_)+"], attributes = ["+str(self.seed_)+", "+str(self.position_)+"], "+", cards = ["+cards+"], metrics = ["+metrics+"])"

    @staticmethod
    def test_execution(point, port, is_sbb):
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

        socket_tmp.send("VERSION:2.0.0\r\n")

        message = socket_tmp.recv(1000)
        message = message.replace("\r\n", "")
        partial_messages = message.split("MATCHSTATE")
        last_message = partial_messages[-1] # only cares about the last message sent (ie. the one where this player should act)
        match_state = MatchState(last_message, PokerConfig.CONFIG['small_bet'], PokerConfig.CONFIG['big_bet'], PokerConfig.full_deck, None)
        action = "f"
        send_msg = "MATCHSTATE"+last_message+":"+action+"\r\n"
        socket_tmp.send(send_msg)
        socket_tmp.close()

        if is_sbb:
            point.sbb_hole_cards = match_state.current_hole_cards
        if not is_sbb:
            point.opponent_hole_cards = match_state.current_hole_cards