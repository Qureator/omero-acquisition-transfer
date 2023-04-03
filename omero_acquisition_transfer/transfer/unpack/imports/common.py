# Copyright (c) 2023 Qureator, Inc. All rights reserved.

from typing import Any

from omero.gateway import BlitzGateway
from omero.rtypes import rstring, rint, rdouble, rlong
from omero.model import LengthI, TimeI
from omero.model.enums import UnitsLength


def update_metadata(obj: Any, name: str, metadata: Any):
    status = False

    if metadata is not None:
        if isinstance(metadata, str):
            metadata = rstring(metadata)
        elif isinstance(metadata, int):
            metadata = rint(metadata)
        elif isinstance(metadata, float):
            metadata = rdouble(metadata)

        setattr(obj, name, metadata)
        status = True

    return status


def update_length_metadata(obj: Any, name: str, metadata: Any, unit: UnitsLength):
    status = False

    if metadata is not None:
        if unit.name in {'SECOND'}:
            setattr(obj, name, TimeI(metadata, unit.name))
        else:
            setattr(obj, name, LengthI(metadata, unit.name))
        status = True

    return status


def update_enum_metadata(obj: Any, name: str, metadata: Any, enum_class_name: str, conn: BlitzGateway):
    status = False

    if metadata is not None:
        if not isinstance(metadata, str):
            metadata = metadata.value

        var = conn.getTypesService().getEnumeration(enum_class_name, metadata)
        setattr(obj, name, var)
        status = True

    return status
