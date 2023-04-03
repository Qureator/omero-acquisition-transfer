# Copyright (c) 2023 Qureator, Inc. All rights reserved.

unit_converter = {
    "NANOMETER": "nm",
    "MICROMETER": "µm",
    "MILLIMETER": "mm",
    "SECOND": "s",
    "REFERENCEFRAME": "reference frame",
}


def convert_units(unit):
    return unit_converter.get(str(unit), unit)
