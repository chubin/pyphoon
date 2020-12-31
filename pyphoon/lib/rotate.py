""" swap table and function for rotating chars 180 degrees.
"""

SWAP_TABLE = str.maketrans(
    "().`_'",
    ")(`.^,"
)

def rotate(char):
    """ Rotate char if it has a "symmetric" char.
    """
    return char.translate(SWAP_TABLE)
