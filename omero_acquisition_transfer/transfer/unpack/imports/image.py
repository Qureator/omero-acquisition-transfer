# Copyright (c) 2023 Qureator, Inc. All rights reserved.

from typing import Dict, Any

from ome_types.model import (
    Image,
    Pixels,
    ObjectiveSettings,
    ImagingEnvironment,
    StageLabel,
)
from omero.gateway import BlitzGateway, ImageWrapper
from omero.model import (
    ObjectiveSettingsI,
    ImagingEnvironmentI,
    StageLabelI,
)
from .channel import attach_channels_metadata
from .common import update_metadata, update_length_metadata, update_enum_metadata


def attach_image_metadata(
        image: Image, image_obj: ImageWrapper, omero_id_to_object: Dict[str, Any], conn: BlitzGateway
) -> None:
    if image is None:
        return None

    if image_obj is None or image_obj._obj is None:
        raise ValueError("image_obj is None")

    update_metadata(image_obj, 'name', image.name)
    update_metadata(image_obj, 'description', image.description)
    # update_metadata(image_obj, 'acquisition_date', image.acquisition_date)

    if image.instrument_ref is not None:
        instrument = omero_id_to_object[image.instrument_ref.id]
        image_obj.setInstrument(instrument)
        image_obj.save()

    if image.objective_settings is not None:
        attach_objective_settings_metadata(image.objective_settings, image_obj, omero_id_to_object, conn)

    if image.imaging_environment is not None:
        attach_imaging_environment_metadata(image.imaging_environment, image_obj, conn)

    if image.pixels is not None:
        attach_pixels_metadata(image.pixels, image_obj, conn, omero_id_to_object)

    if image.stage_label is not None:
        attach_stage_label_metadata(image.stage_label, image_obj, conn)

    # if image.roi_ref is not None:
    #    create_rois(image.roi_ref, ome.rois, image_obj)


def attach_stage_label_metadata(
        stage_label: StageLabel, image_obj: ImageWrapper, conn: BlitzGateway
) -> None:
    sl_obj = StageLabelI()

    update_length_metadata(sl_obj, 'x', stage_label.x, stage_label.x_unit)
    update_length_metadata(sl_obj, 'y', stage_label.y, stage_label.y_unit)
    update_length_metadata(sl_obj, 'z', stage_label.z, stage_label.z_unit)

    image_obj.setStageLabel(sl_obj)

    sl_obj = conn.getUpdateService().saveAndReturnObject(sl_obj)
    image_obj.setStageLabel(sl_obj)
    image_obj.save()


def attach_pixels_metadata(
        pixels: Pixels, image_obj: ImageWrapper, conn: BlitzGateway, omero_id_to_object: Dict[str, Any]
) -> None:
    update_enum_metadata(image_obj, 'dimensionOrder', pixels.dimension_order, 'DimensionOrderI', conn)
    update_enum_metadata(image_obj, 'pixelsType', pixels.type, 'PixelsTypeI', conn)
    update_metadata(image_obj, 'sizeX', pixels.size_x)
    update_metadata(image_obj, 'sizeY', pixels.size_y)
    update_metadata(image_obj, 'sizeZ', pixels.size_z)
    update_metadata(image_obj, 'sizeC', pixels.size_c)
    update_metadata(image_obj, 'sizeT', pixels.size_t)

    attach_channels_metadata(pixels.channels, image_obj, conn, omero_id_to_object)
    image_obj.save()


def attach_objective_settings_metadata(
        objective_settings: ObjectiveSettings,
        image_obj: ImageWrapper,
        omero_id_to_object: Dict[str, Any],
        conn: BlitzGateway
) -> None:
    os_obj = ObjectiveSettingsI()

    update_metadata(os_obj, 'correctionCollar', objective_settings.correction_collar)
    update_enum_metadata(os_obj, 'medium', objective_settings.medium, 'MediumI', conn)
    update_metadata(os_obj, 'refractiveIndex', objective_settings.refractive_index)

    os_obj.setObjective(omero_id_to_object[objective_settings.id])

    os_obj = conn.getUpdateService().saveAndReturnObject(os_obj, conn.SERVICE_OPTS)
    image_obj.setObjectiveSettings(os_obj)
    image_obj.save()


def attach_imaging_environment_metadata(
        imaging_environment: ImagingEnvironment,
        image_obj: ImageWrapper,
        conn: BlitzGateway,
) -> None:
    if imaging_environment is None:
        return None

    ie_obj = ImagingEnvironmentI()

    update_length_metadata(ie_obj, 'temperature', imaging_environment.temperature, imaging_environment.temperature_unit)
    update_length_metadata(ie_obj, 'airPressure', imaging_environment.air_pressure, imaging_environment.air_pressure_unit)
    update_metadata(ie_obj, 'humidity', imaging_environment.humidity)
    update_metadata(ie_obj, 'co2percent', imaging_environment.co2_percent)

    ie_obj = conn.getUpdateService().saveAndReturnObject(ie_obj, conn.SERVICE_OPTS)
    image_obj.setImagingEnvironment(ie_obj)
    image_obj.save()
