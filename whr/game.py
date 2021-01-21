import sys


class Game:
    def __init__(self, black, white, black_points, white_score, time_step, config, handicap=0, extras=None):
        self.day = time_step
        self.white_player = white
        self.black_player = black
        self.black_points = black_points
        self.white_score = white_score
        self.mov = self.white_score - self.black_points
        self.handicap = handicap
        self.handicap_proc = handicap
        self.bpd = None
        self.wpd = None
        self.scale = config["scale"]
        if extras is None:
            self.extras = dict()
            self.extras["komi"] = 6.5
        else:
            self.extras = extras
            if self.extras.get("komi") is None:
                self.extras["komi"] = 6.5

    def gamma(self, val):
        return 10 ** (val / self.scale)

    def opponents_adjusted_gamma(self, player):
        if player == self.white_player:
            opponent_elo = self.bpd.elo + self.handicap
        elif player == self.black_player:
            opponent_elo = self.wpd.elo - self.handicap
        else:
            raise (
                AttributeError(
                    f"No opponent for {player.__str__()}, since they're not in this game: {self.__str__()}."
                )
            )
        rval = self.gamma(opponent_elo)
        if rval == 0 or rval > sys.maxsize:
            raise AttributeError("bad adjusted gamma")
        return rval

    def opponent(self, player):
        if player == self.white_player:
            return self.black_player
        return self.white_player

    def player_mov(self,player):
        if player == self.white_player:
            return self.mov
        return -self.mov
    
    def posterior_win_prob(self,val):
        gval = self.gamma(val)
        return gval / (gval + 1/gval)

    def player_game_gamma(self,player):
        mov = self.player_mov(player)
        p_win_val = self.posterior_win_prob(mov)
        return p_win_val, 1.0-p_win_val

    def prediction_score(self):
        if self.white_win_probability() == 0.5:
            return 0.5
        return (
            1.0
            if (
                (self.mov > 0 and self.white_win_probability() > 0.5)
                or (self.mov <= 0 and self.white_win_probability() < 0.5)
            )
            else 0.0
        )

    def inspect(self):
        return f"W:{self.white_player.name}(r={self.wpd.r if self.wpd is not None else '?'}) B:{self.black_player.name}(r={self.bpd.r if self.bpd is not None else '?'}) mov = {self.mov}, komi = {self.extras['komi']}, handicap = {self.handicap}"

    def white_win_probability(self):
        return self.wpd.gamma() / (
            self.wpd.gamma() + self.opponents_adjusted_gamma(self.white_player)
        )

    def black_win_probability(self):
        return self.bpd.gamma() / (
            self.bpd.gamma() + self.opponents_adjusted_gamma(self.black_player)
        )
