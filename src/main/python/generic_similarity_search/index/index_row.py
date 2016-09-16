class IndexRow(object):
    """
    Encapsulates one row within an index.
    Clients are supposed to create index row objects based on lines of data.
    """

    def __init__(self, pass_throughs: dict, dimensions: dict):
        self.pass_throughs = pass_throughs
        """
        Dictionary of arbitrary name:str and value:str pairs, e.g. for reference (IDs) or convenience.
        A word of caution: the current implementation stores everything in memory!
        Pass through values are not used to calculate distances.
        """

        self.dimensions = dimensions
        """
        Dictionary of name:str and value:float pairs.
        Dimension values are used to calculate distances.
        Dimension value names MUST correspond with weight names.
        """
