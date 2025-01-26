from .constants import chicken_quality_rates

__all__ = ["get_quality_text"]


def get_quality_text(chicken_quality: float) -> str:
    quality = round((chicken_quality * 100) / 10) * 10
    print(quality)
    return chicken_quality_rates[quality]
