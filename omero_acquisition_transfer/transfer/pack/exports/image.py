# Copyright (c) 2023 Qureator, Inc. All rights reserved.

from datetime import datetime
import logging
from typing import Optional, List

from ome_types import OME
from ome_types.model import (
    simple_types,
    Image,
    Pixels,
    InstrumentRef,
    ObjectiveSettings,
    ImagingEnvironment,
    ROIRef,
    StageLabel,
    Plane,
)
from omero.gateway import (
    ImageWrapper,
    BlitzGateway,
)
from omero.model import (
    PixelsI,
    ObjectiveSettingsI,
    ImagingEnvironmentI,
    StageLabelI,
    PlaneInfoI,
)

from .channel import export_channel_metadata
from .common import convert_units
from .instrument import export_instrument_metadata, append_instrument_metadata
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
        logging.info(f"Adding image {id_} to OME")
    else:
        image = ome.images[indices.index(id_)]
        image.name = name
        image.acquisition_date = acquisition_date
        image.description = desc
        image.pixels = pixels
        # image.roi_ref = roi_ref # Not implemented
        logging.info(f"Updating image {id_} in OME")

    if image_obj.getInstrument() is not None:
        instrument_ref: Optional[InstrumentRef] = InstrumentRef(id=image_obj.getInstrument().getId())

        if instrument_ref.id not in [ins.id for ins in ome.instruments]:
            ome.instruments.append(export_instrument_metadata(image_obj.getInstrument()))

        image.instrument_ref = instrument_ref

        # There are some exceptional cases -- Light path has dichroic not within instrument
        # MIP images?
        append_instrument_metadata(ome, image_obj)

    if image_obj.getObjectiveSettings() is not None:
        objective_settings: Optional[ObjectiveSettings] = export_objective_settings_metadata(image_obj.getObjectiveSettings())
        image.objective_settings = objective_settings

    if image_obj.getImagingEnvironment() is not None:
        imaging_environment: Optional[ImagingEnvironment] = export_imaging_environment_metadata(image_obj.getImagingEnvironment())
        image.imaging_environment = imaging_environment

    if image_obj.getStageLabel() is not None:
        stage_label: Optional[StageLabel] = export_stage_label_metadata(image_obj.getStageLabel())
        image.stage_label = stage_label

    if in_place:
        ome.images.append(image)

    return image


def export_plane_metadata(pi_obj: PlaneInfoI) -> Plane:
    plane = Plane(
        the_c=pi_obj.getTheC(),
        the_t=pi_obj.getTheT(),
        the_z=pi_obj.getTheZ(),
    )

    if pi_obj.getDeltaT() is not None:
        plane.delta_t = pi_obj.getDeltaT(units='SECOND').getValue()
        plane.delta_t_unit = convert_units(pi_obj.getDeltaT(units='SECOND').getUnit())

    if pi_obj.getExposureTime() is not None:
        plane.exposure_time = pi_obj.getExposureTime(units='SECOND').getValue()
        plane.exposure_time_unit = convert_units(pi_obj.getExposureTime(units='SECOND').getUnit())

    if pi_obj.getPositionX() is not None:
        plane.position_x = pi_obj.getPositionX().getValue()
        plane.position_x_unit = convert_units(pi_obj.getPositionX().getUnit())

    if pi_obj.getPositionY() is not None:
        plane.position_y = pi_obj.getPositionY().getValue()
        plane.position_y_unit = convert_units(pi_obj.getPositionY().getUnit())

    if pi_obj.getPositionZ() is not None:
        plane.position_z = pi_obj.getPositionZ().getValue()
        plane.position_z_unit = convert_units(pi_obj.getPositionZ().getUnit())

    return plane


def export_stage_label_metadata(sl_obj: StageLabelI) -> Optional[StageLabel]:
    if sl_obj:
        name: str = sl_obj.getName()
        x: Optional[float] = None if not sl_obj.getPositionX() else sl_obj.getPositionX().getValue()
        x_unit: Optional[str] = None if not sl_obj.getPositionX() else sl_obj.getPositionX().getUnit()
        y: Optional[float] = None if not sl_obj.getPositionY() else sl_obj.getPositionY().getValue()
        y_unit: Optional[str] = None if not sl_obj.getPositionY() else sl_obj.getPositionY().getUnit()
        z: Optional[float] = None if not sl_obj.getPositionZ() else sl_obj.getPositionZ().getValue()
        z_unit: Optional[str] = None if not sl_obj.getPositionZ() else sl_obj.getPositionZ().getUnit()

        sl = StageLabel(
            name=name,
        )

        if x is not None:
            sl.x = x
            sl.x_unit = convert_units(x_unit)
        if y is not None:
            sl.y = y
            sl.y_unit = convert_units(y_unit)
        if z is not None:
            sl.z = z
            sl.z_unit = convert_units(z_unit)

        return sl
    return None


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

    if pix_obj.getPhysicalSizeX() is not None:
        pixels.physical_size_x = pix_obj.getPhysicalSizeX().getValue()
        pixels.physical_size_x_unit = convert_units(pix_obj.getPhysicalSizeX().getUnit())
    if pix_obj.getPhysicalSizeY() is not None:
        pixels.physical_size_y = pix_obj.getPhysicalSizeY().getValue()
        pixels.physical_size_y_unit = convert_units(pix_obj.getPhysicalSizeY().getUnit())
    if pix_obj.getPhysicalSizeZ() is not None:
        pixels.physical_size_z = pix_obj.getPhysicalSizeZ().getValue()
        pixels.physical_size_z_unit = convert_units(pix_obj.getPhysicalSizeZ().getUnit())

    for ch_obj in image_obj.getChannels():
        channel = export_channel_metadata(ch_obj)
        pixels.channels.append(channel)

    for pi_obj in image_obj.getPrimaryPixels().copyPlaneInfo():
        plane: Optional[Plane] = export_plane_metadata(pi_obj)
        pixels.planes.append(plane)

    return pixels

