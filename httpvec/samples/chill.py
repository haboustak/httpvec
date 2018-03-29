"""
Chill inspector sample
"""

def select(_, vectors):
    """
    Any vector works, pick the first one
    """
    return vectors[0] if vectors else None
