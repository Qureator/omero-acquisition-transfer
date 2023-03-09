# Copyright (c) 2023 Qureator, Inc. All rights reserved.

from typing import Optional, List

from ome_types.model import (
    Channel,
    LightSourceSettings,
    LightPath, DichroicRef,
    FilterRef,
    Detector, DetectorSettings,
)
from omero.gateway import ChannelWrapper
from omero.model import (
    DetectorSettingsI, DetectorI,
    LightSettingsI, LightPathI,
)

from omero_acquisition_transfer.transfer.pack.export.common import convert_units


def export_channel_metadata(ch_obj: ChannelWrapper):
    lch_obj = ch_obj.getLogicalChannel()

    id_: int = ch_obj.getId()
    name: Optional[str] = lch_obj.getName()
    sample_per_pixel: Optional[int] = lch_obj.getSamplesPerPixel()
    illumination_type: Optional[str] = None if not lch_obj.getIllumination() else lch_obj.getIllumination().getValue()
    pinhole_size: Optional[float] = lch_obj.getPinHoleSize()
    acquisition_mode: Optional[str] = None if not lch_obj.getMode() else lch_obj.getMode().getValue()
    contrast_method: Optional[str] = None if not lch_obj.getContrastMethod() else lch_obj.getContrastMethod().getValue()
    excitation_wavelength: Optional[float] = None if not lch_obj.getExcitationWave() else lch_obj.getExcitationWave().getValue()
    emission_wavelength: Optional[float] = None if not lch_obj.getEmissionWave() else lch_obj.getEmissionWave().getValue()
    fluor: Optional[str] = lch_obj.getFluor()
    nd_filter: Optional[float] = lch_obj.getNdFilter()
    pockel_cell_setting: Optional[int] = lch_obj.getPockelCellSetting()
    color: Optional[str] = None if not ch_obj.getColor() else ch_obj.getColor().getHtml()

    channel = Channel(
        id=id_,
        name=name,
        sample_per_pixel=sample_per_pixel,
        illumination_type=illumination_type,
        pinhole_size=pinhole_size,
        acquisition_mode=acquisition_mode,
        contrast_method=contrast_method,
        excitation_wavelength=excitation_wavelength,
        emission_wavelength=emission_wavelength,
        fluor=fluor,
        nd_filter=nd_filter,
        pockel_cell_setting=pockel_cell_setting,
        color=color,
    )

    # Light path should be called before light source settings
    channel.light_path = export_light_path_metadata(lch_obj.getLightPath())
    channel.light_source_settings = export_light_source_settings_metadata(lch_obj.getLightSourceSettings())
    channel.detector_settings = export_detector_settings_metadata(lch_obj.getDetectorSettings())

    return channel


def export_light_path_metadata(lp_obj: LightPathI) -> Optional[LightPath]:
    if lp_obj is not None:
        if lp_obj.getDichroic() is not None:
            dichroic: Optional[int] = lp_obj.getDichroic().getId()
            dichroic_ref: Optional[DichroicRef] = DichroicRef(id=dichroic)
        else:
            dichroic_ref = None

        emission_filter_ref: Optional[List[FilterRef]] = [
            FilterRef(id=emission_filter.getId())
            for emission_filter in lp_obj.getEmissionFilters()
        ]
        excitation_filter_ref: Optional[List[FilterRef]] = [
            FilterRef(id=excitation_filter.getId())
            for excitation_filter in lp_obj.getExcitationFilters()
        ]

        light_path = LightPath(
            dichroic_ref=dichroic_ref,
            emission_filter_ref=emission_filter_ref,
            excitation_filter_ref=excitation_filter_ref,
        )
        return light_path
    return None


def export_light_source_settings_metadata(lss_obj: LightSettingsI) -> Optional[LightSettingsI]:
    if lss_obj._obj is not None and lss_obj.getLightSource() is not None:
        # Add light source settings
        id_: int = lss_obj.getLightSource().getId()
        attenuation: Optional[float] = lss_obj.getAttenuation()
        wavelength: Optional[float] = None if not lss_obj.getWavelength() else lss_obj.getWavelength().getValue()
        wavelength_unit: Optional[str] = None if not lss_obj.getWavelength() else lss_obj.getWavelength().getUnit()

        lss = LightSourceSettings(
            id=id_,
            attenuation=attenuation,
            wavelength=wavelength,
        )
        if wavelength_unit:
            lss.wavelength_unit = convert_units(wavelength_unit)

        return lss
    return None


def export_detector_settings_metadata(det_set_obj: DetectorSettingsI) -> Optional[DetectorSettings]:
    if det_set_obj._obj is not None and det_set_obj.getDetector() is not None:
        # Add detector
        det_obj: DetectorI = det_set_obj.getDetector()
        detector = export_detector_metadata(det_obj)

        # Add detector settings
        id_: str = detector.id
        offset: Optional[float] = det_set_obj.getOffsetValue()
        gain: Optional[float] = det_set_obj.getGain()
        voltage: Optional[float] = None if not det_set_obj.getVoltage() else det_set_obj.getVoltage().getValue()
        voltage_unit: Optional[float] = None if not det_set_obj.getVoltage() else det_set_obj.getVoltage().getUnit()
        zoom: Optional[float] = det_set_obj.getZoom()
        read_out_rate: Optional[float] = None if not det_set_obj.getReadOutRate() else det_set_obj.getReadOutRate().getValue()
        read_out_rate_unit: Optional[str] = None if not det_set_obj.getReadOutRate() else det_set_obj.getReadOutRate().getUnit()
        binning: Optional[str] = None if not det_set_obj.getBinning() else det_set_obj.getBinning().getValue()
        integration: Optional[int] = det_set_obj.getIntegration()

        detector_settings = DetectorSettings(
            id=id_,
            offset=offset,
            gain=gain,
            voltage=voltage,
            zoom=zoom,
            read_out_rate=read_out_rate,
            binning=binning,
            integration=integration,
        )

        if voltage_unit is not None:
            detector_settings.voltage_unit = convert_units(voltage_unit)

        if read_out_rate_unit is not None:
            detector_settings.read_out_rate_unit = convert_units(read_out_rate_unit)

        return detector_settings
    return None


def export_detector_metadata(det_obj: DetectorI) -> Detector:
    gain: Optional[float] = det_obj.getGain()
    voltage: Optional[float] = None if not det_obj.getVoltage() else det_obj.getVoltage().getValue()
    voltage_unit: Optional[str] = None if not det_obj.getVoltage() else det_obj.getVoltage().getUnit()
    offset: Optional[float] = det_obj.getOffsetValue()
    zoom: Optional[float] = det_obj.getZoom()
    amplification_gain: Optional[float] = det_obj.getAmplificationGain()
    id_: int = det_obj.getId()
    type_: Optional[str] = None if not det_obj.getDetectorType() else det_obj.getDetectorType().getValue()

    if type_ == 'EM-CCD':
        type_ = 'EMCCD'

    # Detector manufacturer spec
    manufacturer: Optional[str] = det_obj.getManufacturer()
    model: Optional[str] = det_obj.getModel()
    serial_number: Optional[str] = det_obj.getSerialNumber()
    lot_number: Optional[str] = det_obj.getLotNumber()

    detector = Detector(
        id=id_,
        gain=gain,
        voltage=voltage,
        offset=offset,
        zoom=zoom,
        amplification_gain=amplification_gain,
        type=type_,
        manufacturer=manufacturer,
        model=model,
        serial_number=serial_number,
        lot_number=lot_number,
    )

    if voltage_unit is not None:
        detector.voltage_unit = convert_units(voltage_unit)

    return detector
