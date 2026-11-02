class Constant:
    def __init__(self, json_dict):
        self._json_dict = json_dict

    @property
    def sizeof_variable_offset(self):
        offset = self._json_dict.get("sizeof")
        if offset is None:
            return None
        return int(offset)

    @property
    def name(self):
        return self._json_dict.get("name")
