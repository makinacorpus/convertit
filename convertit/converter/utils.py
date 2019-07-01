from com.sun.star.beans import PropertyValue


def uno_props(**kwargs):
    """
    A simple way to create libreoffice property values.
    """
    props = []
    for key in kwargs:
        prop = PropertyValue()
        prop.Name = key
        prop.Value = kwargs[key]
        props.append(prop)
    return tuple(props)
