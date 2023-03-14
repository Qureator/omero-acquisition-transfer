# Copyright (c) 2023 Qureator, Inc. All rights reserved.

from datetime import datetime
from typing import Optional, List

from ome_types import OME
from ome_types.model import (
    simple_types,
    Image,
    Pixels,
    InstrumentRef,
    ObjectiveSettings,
    ImagingEnvironment,
    ROIRef
)
from omero.gateway import (
    ImageWrapper,
    BlitzGateway,
)
from omero.model import (
    PixelsI,
    ObjectiveSettingsI,
    ImagingEnvironmentI
)

from .channel import export_channel_metadata
from .common import convert_units
from .instrument import export_instrument_metadata
from .roi import export_attach_rois_metadata


def export_image_metadata(image_obj: ImageWrapper, conn: BlitzGateway, ome: OME, in_place: bool = True) -> Image:
    assert image_obj.getId() is not None, "no image ID"
    assert image_obj.getPrimaryPixels().getId() is not None, "no Pixels ID"

    id_: int = image_obj.getId()
    name: Optional[str] = image_obj.getName()
    acquisition_date: Optional[datetime] = image_obj.getAcquisitionDate()
    desc: Optional[str] = image_obj.getDescription()

    pixels: Pixels = export_pixels_metadata(image_obj)
    rois_ref: Optional[List[ROIRef]] = export_attach_rois_metadata(image_obj, conn, ome)

    indices = [int(img.id.split(':')[-1]) for img in ome.images]

    if id_ not in indices:
        image = Image(
            id=id_,
            name=name,
            acquisition_date=acquisition_date,
            description=desc,
            pixels=pixels,
            # roi_ref=rois_ref,
        )
        print(f"Adding image {id_} to OME")
    else:
        image = ome.images[indices.index(id_)]
        image.name = name
        image.acquisition_date = acquisition_date
        image.description = desc
        image.pixels = pixels
        # image.roi_ref = roi_ref # Not implemented
        print(f"Updating image {id_} in OME")

    if image_obj.getInstrument() is not None:
        instrument_ref: Optional[InstrumentRef] = InstrumentRef(id=image_obj.getInstrument().getId())

        if instrument_ref.id not in [ins.id for ins in ome.instruments]:
            ome.instruments.append(export_instrument_metadata(image_obj.getInstrument()))

        image.instrument_ref = instrument_ref

    if image_obj.getObjectiveSettings() is not None:
        objective_settings: Optional[ObjectiveSettings] = export_objective_settings_metadata(image_obj.getObjectiveSettings())
        image.objective_settings = objective_settings

    if image_obj.getImagingEnvironment() is not None:
        imaging_environment: Optional[ImagingEnvironment] = export_imaging_environment_metadata(image_obj.getImagingEnvironment())
        image.imaging_environment = imaging_environment

    if in_place:
        ome.images.append(image)

    return image


def export_objective_settings_metadata(os_obj: ObjectiveSettingsI) -> Optional[ObjectiveSettings]:
    if os_obj:
        id_: int = os_obj.getObjective().getId()
        correction_collar: Optional[float] = os_obj.getCorrectionCollar()
        medium: Optional[str] = None if not os_obj.getMedium() else os_obj.getMedium().getValue()
        refractive_index: Optional[float] = os_obj.getRefractiveIndex()

        os = ObjectiveSettings(
            id=id_,
            correction_collar=correction_collar,
            medium=medium,
            refractive_index=refractive_index,
        )

        return os
    return None


def export_imaging_environment_metadata(ie_obj: ImagingEnvironmentI) -> Optional[ImagingEnvironment]:
    if ie_obj:
        id_: int = ie_obj.getId()
        air_pressure: Optional[float] = None if not ie_obj.getAirPressure() else ie_obj.getAirPressure().getValue()
        air_pressure_unit: Optional[str] = None if not ie_obj.getAirPressure() else ie_obj.getAirPressure().getUnit()
        co2_percent: Optional[float] = ie_obj.getCo2percent()
        humidity: Optional[float] = ie_obj.getHumidity()
        temperature: Optional[float] = None if not ie_obj.getTemperature() else ie_obj.getTemperature().getValue()
        temperature_unit: Optional[str] = None if not ie_obj.getTemperature() else ie_obj.getTemperature().getUnit()

        ie = ImagingEnvironment(
            id=id_,
            air_pressure=air_pressure,
            co2_percent=co2_percent,
            humidity=humidity,
            temperature=temperature,
        )

        if air_pressure_unit:
            ie.air_pressure_unit = convert_units(air_pressure_unit)
        if temperature_unit:
            ie.temperature_unit = convert_units(temperature_unit)

        return ie
    return None


def export_pixels_metadata(image_obj: ImageWrapper) -> Pixels:
    pix_obj: PixelsI = image_obj.getPrimaryPixels()
    pixel_type = image_obj.getPixelsType()
    try:
        pixel_type = simple_types.PixelType(pixel_type)
    except:
        raise ValueError(f"Invalid pixel type: {pixel_type}")

    pixels = Pixels(
        id=image_obj.getId(),
        dimension_order=pix_obj.getDimensionOrder().getValue(),
        size_c=pix_obj.getSizeC(),
        size_t=pix_obj.getSizeT(),
        size_x=pix_obj.getSizeX(),
        size_y=pix_obj.getSizeY(),
        size_z=pix_obj.getSizeZ(),
        type=pix_obj.getPixelsType().getValue(),
        metadata_only=True)

    for ch_obj in image_obj.getChannels():
        channel = export_channel_metadata(ch_obj)
        pixels.channels.append(channel)

    return pixels

