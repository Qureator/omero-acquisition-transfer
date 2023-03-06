unit_converter = {
    "NANOMETER": "nm",
    "MICROMETER": "µm",
    "MILLIMETER": "mm",
}


def convert_units(unit):
    return unit_converter.get(str(unit), unit)
