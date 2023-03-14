# Copyright (c) 2023 Qureator, Inc. All rights reserved.

from typing import List, Optional, Dict, Any

from ome_types.model import (
    Channel,
    LightSourceSettings,
    LightPath,
    DetectorSettings,
)
from omero.gateway import (
    BlitzGateway,
    ImageWrapper,
    LightPathWrapper,
    LightSettingsWrapper,
    DetectorSettingsWrapper,
    LogicalChannelWrapper
)
from omero.model import (
    ChannelI, LightPathI, LightPathEmissionFilterLinkI, LightPathExcitationFilterLinkI,
    LightSettingsI,
    DetectorSettingsI,
)

from .common import update_metadata, update_length_metadata, update_enum_metadata


def attach_channels_metadata(
        channels: List[Channel],
        image_obj: ImageWrapper,
        conn: BlitzGateway,
        omero_id_to_obj: Dict[str, Any]
) -> None:
    channel_objs = image_obj.getChannels()

    assert len(channel_objs) == len(channels), f'Number of channels in image {image_obj.id} {len(channels)} ' \
                                               f'does not match number of channels {len(channel_objs)} in OME-TIFF'

    for ch_obj, channel in zip(channel_objs, channels):
        ch_obj = attach_channel_metadata(channel, ch_obj, conn, omero_id_to_obj)


def attach_channel_metadata(
        channel: Channel, ch_obj: ChannelI, conn: BlitzGateway, omero_id_to_obj: Dict[str, Any]
) -> ChannelI:
    lch_obj = attach_logical_channel_metadata(channel, ch_obj.getLogicalChannel(), conn, omero_id_to_obj)
    ch_obj.setLogicalChannel(lch_obj._obj)
    ch_obj.save()

    return ch_obj


def attach_logical_channel_metadata(
        channel: Channel, lch_obj: LogicalChannelWrapper, conn: BlitzGateway, omero_id_to_obj: Dict[str, Any]
) -> LogicalChannelWrapper:
    update_metadata(lch_obj, 'name', channel.name)
    update_metadata(lch_obj, 'samplesPerPixel', channel.samples_per_pixel)
    update_enum_metadata(lch_obj, 'illumination', channel.illumination_type, 'IlluminationI', conn)
    update_metadata(lch_obj, 'pinHoleSize', channel.pinhole_size)
    update_enum_metadata(lch_obj, 'mode', channel.acquisition_mode, 'AcquisitionModeI', conn)
    update_enum_metadata(lch_obj, 'contrastMethod', channel.contrast_method, 'ContrastMethodI', conn)
    update_length_metadata(lch_obj, 'excitationWave', channel.excitation_wavelength, channel.excitation_wavelength_unit)
    update_length_metadata(lch_obj, 'emissionWave', channel.emission_wavelength, channel.emission_wavelength_unit)
    update_metadata(lch_obj, 'fluor', channel.fluor)
    update_metadata(lch_obj, 'ndFilter', channel.nd_filter)
    update_metadata(lch_obj, 'pockelCellSetting', channel.pockel_cell_setting)

    lp_obj: LightPathWrapper = create_light_path(channel.light_path, lch_obj.getLightPath(), conn, omero_id_to_obj)
    if lp_obj is not None:
        lch_obj.setLightPath(lp_obj._obj)

    lss_obj: LightSettingsWrapper = create_light_source_settings(channel.light_source_settings, lch_obj.getLightSourceSettings(), omero_id_to_obj, conn)
    if lss_obj is not None:
        lch_obj.setLightSourceSettings(lss_obj._obj)

    det_obj: DetectorSettingsWrapper = create_detector_settings(channel.detector_settings, lch_obj.getDetectorSettings(), omero_id_to_obj, conn)
    if det_obj is not None:
        lch_obj.setDetectorSettings(det_obj._obj)

    lch_obj.save()

    return lch_obj


def create_light_path(
        light_path: LightPath,
        lp_obj: LightPathWrapper,
        conn: BlitzGateway,
        omero_id_to_obj: Dict[str, Any]
) -> Optional[LightPathWrapper]:
    if light_path is None:
        return None

    if lp_obj is None:
        lp_obj = LightPathWrapper(conn, LightPathI())
        lp_obj.save()

    if light_path.dichroic_ref is not None:
        dichroic_obj = omero_id_to_obj[light_path.dichroic_ref.id]
        lp_obj.setDichroic(dichroic_obj)

    if len(light_path.emission_filter_ref) > 0:
        # Remove existing links
        for link in lp_obj.copyEmissionFilterLink():
            lp_obj.removeLightPathEmissionFilterLink(link)

        for f in light_path.emission_filter_ref:
            filter_obj = omero_id_to_obj[f.id]
            link = LightPathEmissionFilterLinkI()
            link.setParent(lp_obj)
            link.setChild(filter_obj)
            lp_obj.addLightPathEmissionFilterLink(link)

    if len(light_path.excitation_filter_ref) > 0:
        for link in lp_obj.copyExcitationFilterLink():
            lp_obj.removeLightPathExcitationFilterLink(link)

        for f in light_path.excitation_filter_ref:
            filter_obj = omero_id_to_obj[f.id]
            link = LightPathExcitationFilterLinkI()
            link.setParent(lp_obj)
            link.setChild(filter_obj)
            lp_obj.addLightPathExcitationFilterLink(link)

    lp_obj.save()
    return lp_obj


def create_light_source_settings(
        light_source_settings: LightSourceSettings,
        lss_obj: LightSettingsI,
        omero_id_to_obj: Dict[str, Any],
        conn: BlitzGateway,
) -> Optional[LightSettingsWrapper]:
    if light_source_settings is None:
        return None

    if lss_obj is None or lss_obj._obj is None:
        lss_obj = LightSettingsWrapper(conn, LightSettingsI())
        lss_obj.setLightSource(omero_id_to_obj[light_source_settings.id])
        lss_obj.save()

    update_length_metadata(lss_obj._obj, 'wavelength', light_source_settings.wavelength, light_source_settings.wavelength_unit)
    update_metadata(lss_obj._obj, 'attenuation', light_source_settings.attenuation)

    lss_obj.save()
    return lss_obj


def create_detector_settings(
        detector_settings: DetectorSettings,
        det_obj: DetectorSettingsWrapper,
        omero_id_to_obj: Dict[str, Any],
        conn: BlitzGateway,
) -> Optional[DetectorSettingsWrapper]:
    if detector_settings is None:
        return None

    if det_obj is None or det_obj._obj is None:
        det_obj = DetectorSettingsWrapper(conn, DetectorSettingsI())
        det_obj.setDetector(omero_id_to_obj[detector_settings.id])
        det_obj.save()

    update_metadata(det_obj._obj, 'gain', detector_settings.gain)
    update_metadata(det_obj._obj, 'offsetValue', detector_settings.offset)
    update_metadata(det_obj._obj, 'readOutRate', detector_settings.read_out_rate)
    update_length_metadata(det_obj._obj, 'voltage', detector_settings.voltage, detector_settings.voltage_unit)
    update_enum_metadata(det_obj._obj, 'binning', detector_settings.binning, 'BinningI', conn)
    update_metadata(det_obj._obj, 'zoom', detector_settings.zoom)

    det_obj.save()
    return det_obj
