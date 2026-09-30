from tools.constants import ELO_K_DEFAULT, ELO_K_PLACEMENT, ELO_K_TOP_RANK
from tools.services import EloRatingService


class TestEloRatingService:

    def test_even_match_moves_half_of_k(self):
        change = EloRatingService.rating_change(500, 500, winner_k=40, loser_k=40)

        assert change.winner_gain == 20
        assert change.loser_loss == 20

    def test_upset_is_worth_more_than_expected_win(self):
        upset = EloRatingService.rating_change(300, 700, winner_k=40, loser_k=40)
        expected_win = EloRatingService.rating_change(700, 300, winner_k=40, loser_k=40)

        assert upset.winner_gain == 36
        assert expected_win.winner_gain == 4

    def test_same_k_is_zero_sum(self):
        change = EloRatingService.rating_change(640, 410, winner_k=40, loser_k=40)

        assert change.winner_gain == change.loser_loss

    def test_huge_gap_still_gives_at_least_one(self):
        change = EloRatingService.rating_change(3000, 100, winner_k=40, loser_k=40)

        assert change.winner_gain == 1
        assert change.loser_loss == 1

    def test_loser_never_drops_below_zero(self):
        # Near-even match, so Elo says the loser drops ~20, but they only have 5 MMR.
        change = EloRatingService.rating_change(0, 5, winner_k=40, loser_k=40)

        assert change.loser_loss == 5

    def test_loser_never_gains(self):
        # The old formula let a loser gain MMR once the gap passed BASE_MMR_CHANGE².
        for gap in range(0, 3000, 50):
            assert EloRatingService.rating_change(1000 + gap, 1000, 40, 40).loser_loss >= 1

    def test_k_factor_tiers(self):
        assert EloRatingService.k_factor(500, games_played=3) == ELO_K_PLACEMENT
        assert EloRatingService.k_factor(500, games_played=100) == ELO_K_DEFAULT
        assert EloRatingService.k_factor(1000, games_played=100) == ELO_K_TOP_RANK
        assert EloRatingService.k_factor(500, games_played=None) == ELO_K_DEFAULT  # bots
