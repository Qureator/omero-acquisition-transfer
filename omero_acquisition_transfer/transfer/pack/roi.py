from typing import Optional, List

from ome_types import OME
from ome_types.model import (
    ROI, ROIRef, Shape, Point, Line, Rectangle, Polygon, Polyline, Ellipse, Label
)
from omero.gateway import (
    ImageWrapper,
    BlitzGateway,
    RoiWrapper,
)
from omero.model import (
    RoiI, PointI, LineI, RectangleI, PolygonI, PolylineI, EllipseI, MaskI, LabelI
)


def export_attach_rois_metadata(image_obj: ImageWrapper, conn: BlitzGateway, ome: OME) -> Optional[List[ROIRef]]:
    roi_service = conn.getRoiService()
    rois_obj = roi_service.findByImage(image_obj.getId(), None).rois
    rois_ref = []

    if rois_obj:
        for roi_obj in rois_obj:
            roi = export_roi_metadata(roi_obj)
            if roi:
                roi_ref = ROIRef(id=roi_obj.getId().getValue())
                rois_ref.append(roi_ref)
                ome.rois.append(roi)

    return rois_ref


def export_roi_metadata(roi_obj: RoiWrapper) -> Optional[ROI]:
    id_: int = roi_obj.getId().getValue()
    name: Optional[str] = None if not roi_obj.getName() else roi_obj.getName().getValue()
    desc: Optional[str] = None if not roi_obj.getDescription() else roi_obj.getDescription().getValue()

    shapes = export_shapes_metadata(roi_obj)
    if not shapes:
        return None

    roi = ROI(
        id=id_,
        name=name,
        description=desc,
        union=shapes,
    )

    return roi


def export_shapes_metadata(roi_obj: RoiWrapper) -> Optional[List[Shape]]:
    shapes: List[Shape] = []

    for s_obj in roi_obj.copyShapes():
        shape = export_shape_metadata(s_obj)
        if shape:
            shapes.append(shape)

    return shapes


def export_shape_metadata(s_obj) -> Optional[Shape]:
    if s_obj:
        args = {
            'id': s_obj.getId().getValue(),
            'fill_color': None if not s_obj.getFillColor() else s_obj.getFillColor().getValue(),
            'fill_rule': None if not s_obj.getFillRule() else s_obj.getFillRule().getValue(),
            'stroke_color': None if not s_obj.getStrokeColor() else s_obj.getStrokeColor().getValue(),
            'stroke_width': None if not s_obj.getStrokeWidth() else s_obj.getStrokeWidth().getValue(),
            'stroke_dash_array': None if not s_obj.getStrokeDashArray() else s_obj.getStrokeDashArray().getValue(),
            'label': None if not s_obj.getTextValue() else s_obj.getTextValue().getValue(),
            'font_family': None if not s_obj.getFontFamily() else s_obj.getFontFamily().getValue(),
            'font_size': None if not s_obj.getFontSize() else s_obj.getFontSize().getValue(),
            'font_style': None if not s_obj.getFontStyle() else s_obj.getFontStyle().getValue(),
            'locked': s_obj.getLocked(),
            'the_t': None if not s_obj.getTheT() else s_obj.getTheT().getValue(),
            'the_z': None if not s_obj.getTheZ() else s_obj.getTheZ().getValue(),
            'the_c': None if not s_obj.getTheC() else s_obj.getTheC().getValue(),
        }

        if isinstance(s_obj, PointI):
            args['x']: Optional[float] = None if not s_obj.getX() else s_obj.getX().getValue()
            args['y']: Optional[float] = None if not s_obj.getY() else s_obj.getY().getValue()
            shape = Point(**args)
        elif isinstance(s_obj, LineI):
            args['x1']: Optional[float] = None if not s_obj.getX1() else s_obj.getX1().getValue()
            args['x2']: Optional[float] = None if not s_obj.getX2() else s_obj.getX2().getValue()
            args['y1']: Optional[float] = None if not s_obj.getY1() else s_obj.getY1().getValue()
            args['y2']: Optional[float] = None if not s_obj.getY2() else s_obj.getY2().getValue()
            shape = Line(**args)
        elif isinstance(s_obj, RectangleI):
            args['x']: Optional[float] = None if not s_obj.getX() else s_obj.getX().getValue()
            args['y']: Optional[float] = None if not s_obj.getY() else s_obj.getY().getValue()
            args['width']: Optional[float] = None if not s_obj.getWidth() else s_obj.getWidth().getValue()
            args['height']: Optional[float] = None if not s_obj.getHeight() else s_obj.getHeight().getValue()
            shape = Rectangle(**args)
        elif isinstance(s_obj, EllipseI):
            args['x']: Optional[float] = None if not s_obj.getX() else s_obj.getX().getValue()
            args['y']: Optional[float] = None if not s_obj.getY() else s_obj.getY().getValue()
            args['radius_x']: Optional[float] = None if not s_obj.getRadiusX() else s_obj.getRadiusX().getValue()
            args['radius_y']: Optional[float] = None if not s_obj.getRadiusY() else s_obj.getRadiusY().getValue()
            shape = Ellipse(**args)
        elif isinstance(s_obj, PolygonI):
            args['points']: Optional[str] = None if not s_obj.getPoints() else s_obj.getPoints().getValue()
            shape = Polygon(**args)
        elif isinstance(s_obj, PolylineI):
            args['points']: Optional[str] = None if not s_obj.getPoints() else s_obj.getPoints().getValue()
            shape = Polyline(**args)
        elif isinstance(s_obj, LabelI):
            args['x']: Optional[float] = None if not s_obj.getX() else s_obj.getX().getValue()
            args['y']: Optional[float] = None if not s_obj.getY() else s_obj.getY().getValue()
            shape = Label(**args)
        elif isinstance(s_obj, MaskI):
            print('Mask ROIs are not implemented')
            shape = MaskI(**args)
        else:
            raise NotImplementedError('Unknown ROI type: %s' % s_obj.__class__.__name__)

        return shape
    return None
