import patterns.characteristics as characteristics


class Constants:
    def __init__(self, json_dict):
        self._constants = {}
        for str_value, constant_dict in json_dict.items():
            # Floating point values have decimal point: "10.0"
            if "." in str_value:
                value = float(str_value)
            else:
                value = int(str_value)
            self._constants[value] = characteristics.Constant(constant_dict)

    def by_value(self, value):
        return self._constants.get(value)

    def float_by_value(self, value):
        """Return characteristics of floating point constant."""
        for key, constant in self._constants.items():
            if isinstance(key, float) and key == value:
                return constant
        return None
