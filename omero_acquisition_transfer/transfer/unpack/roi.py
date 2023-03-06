from typing import Any, Dict, List
from ome_types.model import (
    ROIRef, ROI
)
from omero.model import (
    RoiI
)
from omero.gateway import BlitzGateway, ImageWrapper


def create_rois(
        rois: List[ROI], conn: BlitzGateway
) -> Dict[str, Any]:
    # TODO: implement
    pass
