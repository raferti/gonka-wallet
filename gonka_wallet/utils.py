from .const import NGONKA_PER_GONKA


def gonka_to_ngonka(amount: float) -> int:
    return int(amount * NGONKA_PER_GONKA)


def ngonka_to_gonka(amount: int) -> float:
    return amount / NGONKA_PER_GONKA
