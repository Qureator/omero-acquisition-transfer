from typing import List

import ezomero
from ezomero import rois
from ome_types.model import (
    ROI, Image, Shape,
    Point, Line, Rectangle, Ellipse, Polygon, Polyline, Label
)
from ome_types.model.simple_types import Marker
from omero.gateway import BlitzGateway


def create_rois(rois: List[ROI], imgs: List[Image], img_map: dict,
                conn: BlitzGateway):
    for img in imgs:
        for roiref in img.roi_ref:
            roi = next(filter(lambda x: x.id == roiref.id, rois))
            shapes = create_shapes(roi)
            if roi.union[0].fill_color:
                fc = roi.union[0].fill_color.as_rgb_tuple()
                if len(fc) == 3:
                    fill_color = fc + (255,)
                else:
                    alpha = fc[3] * 255
                    fill_color = fc[0:3] + (int(alpha),)
            else:
                fill_color = (0, 0, 0, 0)
            if roi.union[0].stroke_color:
                sc = roi.union[0].stroke_color.as_rgb_tuple()
                if len(sc) == 3:
                    stroke_color = sc + (255,)
                else:
                    stroke_color = sc
            else:
                stroke_color = (255, 255, 255, 255)
            if roi.union[0].stroke_width:
                stroke_width = int(roi.union[0].stroke_width)
            else:
                stroke_width = 1
            img_id_dest = img_map[img.id]
            ezomero.post_roi(conn, img_id_dest, shapes, name=roi.name,
                             description=roi.description,
                             fill_color=fill_color, stroke_color=stroke_color,
                             stroke_width=stroke_width)


def create_shapes(roi: ROI) -> List[Shape]:
    shapes = []
    for shape in roi.union:
        if isinstance(shape, Point):
            sh = rois.Point(shape.x, shape.y, z=shape.the_z, c=shape.the_c,
                            t=shape.the_t, label=shape.text)
        elif isinstance(shape, Line):
            if shape.marker_start == Marker.ARROW:
                mk_start = "Arrow"
            else:
                mk_start = str(shape.marker_start)
            if shape.marker_end == Marker.ARROW:
                mk_end = "Arrow"
            else:
                mk_end = str(shape.marker_end)
            sh = rois.Line(shape.x1, shape.y1, shape.x2, shape.y2,
                           z=shape.the_z, c=shape.the_c, t=shape.the_t,
                           label=shape.text, markerStart=mk_start,
                           markerEnd=mk_end)
        elif isinstance(shape, Rectangle):
            sh = rois.Rectangle(shape.x, shape.y, shape.width, shape.height,
                                z=shape.the_z, c=shape.the_c, t=shape.the_t,
                                label=shape.text)
        elif isinstance(shape, Ellipse):
            sh = rois.Ellipse(shape.x, shape.y, shape.radius_x, shape.radius_y,
                              z=shape.the_z, c=shape.the_c, t=shape.the_t,
                              label=shape.text)
        elif isinstance(shape, Polygon):
            points = []
            for pt in shape.points.split(" "):
                # points sometimes come with a comma at the end...
                pt = pt.rstrip(",")
                points.append(tuple(float(x) for x in pt.split(",")))
            sh = rois.Polygon(points, z=shape.the_z, c=shape.the_c,
                              t=shape.the_t, label=shape.text)
        elif isinstance(shape, Polyline):
            points = []
            for pt in shape.points.split(" "):
                # points sometimes come with a comma at the end...
                pt = pt.rstrip(",")
                points.append(tuple(float(x) for x in pt.split(",")))
            sh = rois.Polyline(points, z=shape.the_z, c=shape.the_c,
                               t=shape.the_t, label=shape.text)
        elif isinstance(shape, Label):
            sh = rois.Label(shape.x, shape.y, z=shape.the_z, c=shape.the_c,
                            t=shape.the_t, label=shape.text,
                            fontSize=shape.font_size)
        else:
            continue
        shapes.append(sh)
    return shapes
