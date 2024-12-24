# utils/calculate_odds.py

from typing import Union

def decimal_to_fractional(decimal_odds: float) -> str:
    """
    Convert decimal odds to fractional odds.
    Example: 2.5 -> '3/2'
    """
    numerator = int((decimal_odds - 1) * 100)
    denominator = 100
    gcd = _find_gcd(numerator, denominator)
    return f"{numerator // gcd}/{denominator // gcd}"

def fractional_to_decimal(fractional_odds: str) -> float:
    """
    Convert fractional odds to decimal odds.
    Example: '3/2' -> 2.5
    """
    numerator, denominator = map(int, fractional_odds.split('/'))
    return (numerator / denominator) + 1

def american_to_decimal(american_odds: int) -> float:
    """
    Convert American odds to decimal odds.
    Positive values are underdogs, and negative values are favorites.
    """
    if american_odds > 0:
        return (american_odds / 100) + 1
    else:
        return (100 / abs(american_odds)) + 1

def decimal_to_american(decimal_odds: float) -> Union[int, str]:
    """
    Convert decimal odds to American odds.
    Returns +value if decimal odds indicate an underdog.
    Returns -value if decimal odds indicate a favorite.
    """
    if decimal_odds >= 2.0:
        return int((decimal_odds - 1) * 100)
    elif decimal_odds > 1:
        return int(-100 / (decimal_odds - 1))
    else:
        return "Invalid decimal odds"

def implied_probability(decimal_odds: float) -> float:
    """
    Calculate implied probability from decimal odds.
    Example: 2.5 -> 40.0 (percent)
    """
    return (1 / decimal_odds) * 100

def calculate_payout(stake: float, decimal_odds: float) -> float:
    """
    Calculate potential payout based on the stake and decimal odds.
    """
    return stake * decimal_odds

def calculate_profit(stake: float, decimal_odds: float) -> float:
    """
    Calculate potential profit based on the stake and decimal odds.
    """
    return (decimal_odds - 1) * stake

def is_valid_odds(decimal_odds: float) -> bool:
    """
    Validate if the decimal odds are positive and above 1.0 (1.0 means no return).
    """
    return decimal_odds > 1.0

def _find_gcd(a: int, b: int) -> int:
    """
    Helper function to find the greatest common divisor (GCD) of two numbers.
    """
    while b:
        a, b = b, a % b
    return a
