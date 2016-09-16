from generic_similarity_search.api.row import Row
from generic_similarity_search.index.index_row import IndexRow


class Index(object):
    """
    Internal abstraction for weights as well as all data rows of an Index.
    Clients are not supposed to use or create Index objects directly.
    """

    def __init__(self, config: dict):
        self.rows = []
        self.config = config

    def append_row(self, row: Row):
        dimensions = {}
        pass_throughs = {}

        for field_name, field_config in self.config.items():
            field_value = row.fields[field_name]
            to_index_value_function, _ = field_config.get("mapper", (float, None))

            if field_config["index"]:
                dimensions[field_name] = to_index_value_function(field_value)
            else:
                pass_throughs[field_name] = field_value

        self.rows.append(IndexRow(pass_throughs, dimensions))
