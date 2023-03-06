# Copyright (c) 2023 Qureator, Inc. All rights reserved.

from typing import Dict, Any

from ome_types.model import (
    Image,
    Pixels,
    ObjectiveSettings,
    ImagingEnvironment,
)
from omero.gateway import BlitzGateway, ImageWrapper
from omero.model import (
    ObjectiveSettingsI,
    ImagingEnvironmentI,
)
from omero_acquisition_transfer.transfer.unpack.channel import attach_channels_metadata
from omero_acquisition_transfer.transfer.unpack.common import update_metadata, update_length_metadata, update_enum_metadata


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

    if image.objective_settings is not None:
        attach_objective_settings_metadata(image.objective_settings, image_obj, omero_id_to_object, conn)

    if image.imaging_environment is not None:
        attach_imaging_environment_metadata(image.imaging_environment, image_obj, conn)

    if image.pixels is not None:
        attach_pixels_metadata(image.pixels, image_obj, conn, omero_id_to_object)

    # if image.roi_ref is not None:
    #    create_rois(image.roi_ref, ome.rois, image_obj)

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
