import data_types
from exceptions import UnknownTypeException


def parse_data_type(s, classes):
    if s == "real64":
        return data_types.Double()
    if s == "real32":
        return data_types.Float()
    if s == "void":
        return None
    if s.startswith("const"):
        data_type = parse_data_type(s[5:].strip(), classes)
        data_type.add_qualifier("const")
        return data_type
    if s.endswith("const"):
        data_type = parse_data_type(s[:-5].strip(), classes)
        assert isinstance(
            data_type, (data_types.Pointer32, data_types.Reference))
        data_type.add_right_qualifier("const")
        return data_type
    class_name = _extract_class_name(s)
    if class_name is not None:
        if class_name not in classes:
            raise UnknownTypeException("Unknown class: {}.".format(class_name))
        return data_types.Pointer32(classes[class_name])
    if s in classes:
        return classes[s]
    if s.endswith("*"):
        return _parse_const(data_types.Pointer32, s[:-1], classes)
    if s.endswith("&"):
        return _parse_const(data_types.Reference, s[:-1], classes)
    if s.endswith(">"):
        return _parse_template(s, classes)
    sep_pos = s.find("::")
    if sep_pos >= 0:
        namespace_type = parse_data_type(s[:sep_pos], classes)
        data_type = parse_data_type(s[sep_pos + 2:], classes)
        data_type.set_namespace(namespace_type)
        return data_type
    raise UnknownTypeException("Not implemented type: {}.".format(s))


def _parse_const(cb, s, classes):
    s = s.strip()
    is_const = False
    if s.endswith("const"):
        s = s[:-5].strip()
        is_const = True
    data_type = cb(parse_data_type(s, classes))
    if is_const:
        assert isinstance(
            data_type, (data_types.Pointer32, data_types.Reference))
        data_type.add_qualifier("const")
    return data_type


def _extract_class_name(class_type):
    if class_type is None:
        return None
    type_tokens = class_type.split(" ")
    if type_tokens[0] != "struct":
        return None
    if type_tokens[-1] != "*":
        raise Exception("Only pointers is supported for thiscall parameter.")
    class_name = type_tokens[1]
    if len(type_tokens) != 3:
        raise Exception(
            "Failed to extract class name from '{}'.".format(class_type)
        )
    return class_name


def _parse_template(s, classes):
    start_pos = s.find("<")
    if start_pos < 0:
        raise Exception("'<' was not found at {}.".format(s))
    template_type = parse_data_type(s[:start_pos], classes)
    template_arg = parse_data_type(s[start_pos + 1:-1], classes)
    if template_arg is not None:
        template_arg_name = template_arg.get_type_name()
    else:
        template_arg_name = "void"
    new_name = "{}<{}>".format(template_type.class_name, template_arg_name)
    if template_type.template_param is not None and template_arg is not None:
        return template_type.instantiate(new_name, template_arg)
    return template_type.rename(new_name)
