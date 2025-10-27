"""
SafeString class for marking content as safe (already escaped/trusted)
"""


class SafeString(str):
    """
    A string subclass that marks content as safe (already escaped/trusted)
    Used for slot content to prevent double-escaping
    """
    pass
