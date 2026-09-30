from typing import NamedTuple, Optional
from tools.constants import (
    ELO_SCALE,
    ELO_PLACEMENT_MATCHES,
    ELO_K_PLACEMENT,
    ELO_K_DEFAULT,
    ELO_K_TOP_RANK,
    MMR_PER_RANK,
    RANKS,
)

__all__ = ["EloRatingService", "MmrChange"]

_TOP_RANK_MMR = MMR_PER_RANK * (len(RANKS) - 1)


class MmrChange(NamedTuple):
    winner_gain: int
    loser_loss: int


class EloRatingService:
    """Elo rating, the system chess (FIDE) uses and that most competitive games' MMR is based on.

    Each side's expected score comes from the rating gap. After a match, a side's rating moves
    by K * (actual score - expected score). Beating a stronger opponent is worth a lot, beating a
    much weaker one is worth almost nothing, and losing to a weaker one costs a lot.
    """

    @staticmethod
    def expected_score(mmr: int, opponent_mmr: int) -> float:
        """Probability (0-1) that the side with `mmr` beats the side with `opponent_mmr`."""
        return 1 / (1 + 10 ** ((opponent_mmr - mmr) / ELO_SCALE))

    @staticmethod
    def k_factor(mmr: int, games_played: Optional[int]) -> int:
        """How far one match can move this rating. `games_played` is None for bots."""
        if games_played is not None and games_played < ELO_PLACEMENT_MATCHES:
            return ELO_K_PLACEMENT
        if mmr >= _TOP_RANK_MMR:
            return ELO_K_TOP_RANK
        return ELO_K_DEFAULT

    @staticmethod
    def rating_change(winner_mmr: int, loser_mmr: int, winner_k: int, loser_k: int) -> MmrChange:
        """MMR the winner gains and the loser loses. Each side uses its own K, as in FIDE ratings.

        Every result moves both ratings by at least 1, and the loser never drops below 0 MMR.
        """
        winner_expected = EloRatingService.expected_score(winner_mmr, loser_mmr)

        gain = max(1, round(winner_k * (1 - winner_expected)))
        loss = max(1, round(loser_k * (1 - winner_expected)))

        return MmrChange(winner_gain=gain, loser_loss=min(loss, max(loser_mmr, 0)))
