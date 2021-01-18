import math
import sys


class PlayerDay:
    def __init__(self, player, day, config):
        self.scale = config["scale"]
        self.day = day
        self.player = player
        self.is_first_day = False
        self.mov_games = []
        self._mov_game_terms = None

    def set_gamma(self, value):
        self.r = math.log(value)

    def gamma(self):
        return math.exp(self.r)

    @property
    def elo(self):
        return (self.r * self.scale) / (math.log(10))

    @elo.setter
    def elo(self, value):
        self.r = value * (math.log(10) / self.scale)

    def clear_game_terms_cache(self):
        self._mov_game_terms = None

    def mov_game_terms(self):
        if self._mov_game_terms is None:
            self._mov_game_terms = []
            for g in self.mov_games:
                other_gamma = g.opponents_adjusted_gamma(self.player)
                if other_gamma == 0 or other_gamma is None or other_gamma > sys.maxsize:
                    print(
                        f"other_gamma ({g.opponent(self.player).__str__()}) = {other_gamma}"
                    )
                print(other_gamma)
                mov = g.player_mov(self.player)
                a_gamma = 10 ** (mov / self.scale)
                b_gamma = 10 ** (-mov / self.scale)
                sum_gamma = a_gamma + b_gamma
                a_gamma = a_gamma/sum_gamma
                b_gamma = b_gamma/sum_gamma
                self._mov_game_terms.append([a_gamma, b_gamma, a_gamma, other_gamma])
            if self.is_first_day:
                # win against virtual player ranked with gamma = 1.0
                self._mov_game_terms.append([1.0, 0.0, 1.0, 1.0])
        return self._mov_game_terms

    def log_likelihood_second_derivative(self):
        result = 0.0
        for a, b, c, d in self.mov_game_terms():
            result += - (a * b) / ((a * self.gamma() + b) ** 2.0) + (c * d) / ((c * self.gamma() + d) ** 2.0)
        return -1 * self.gamma() * result

    def log_likelihood_derivative(self):
        tally = 0.0
        for a, b, c, d in self.mov_game_terms():
            tally += a / (a * self.gamma() + b) - c / (c * self.gamma() + d)
        return self.gamma() * tally

    def log_likelihood(self):
        tally = 0.0
        for a, b, c, d in self.mov_game_terms():
            tally += math.log(a * self.gamma() + b)
            tally -= math.log(c * self.gamma() + d)
        return tally

    def add_game(self, game):
        self.mov_games.append(game)

    def update_by_1d_newtons_method(self):
        dlogp = self.log_likelihood_derivative()
        d2logp = self.log_likelihood_second_derivative()
        dr = dlogp / d2logp
        new_r = self.r - dr
        self.r = new_r
