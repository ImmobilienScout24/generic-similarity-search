class Row(object):
    """
    Encapsulates one row
    Clients are supposed to create row objects based on lines of data.
    """

    def __init__(self, index_name: str, fields: dict):
        self.index_name = index_name
        """Name of index as used by clients."""

        self.fields = fields
        """
        Dictionary of name:str and value:float pairs.
        """
