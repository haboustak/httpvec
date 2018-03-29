"""
Chaos inspector sample
"""
import random

def select(_, vectors):
    """
    Select random vector
    """
    return random.SystemRandom().choice(vectors) if vectors else None
