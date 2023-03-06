# Copyright (c) 2023 Qureator, Inc. All rights reserved.

from typing import Optional, List

from ome_types.model import (
    Instrument,
    Objective,
    Microscope,
    LightSource,
    Laser, LightEmittingDiode, Arc, Filament, GenericExcitationSource,
    Detector,
    Filter, TransmittanceRange,
    Dichroic,
)
from omero.model import (
    InstrumentI,
    ObjectiveI,
    MicroscopeI,
    LaserI, LightEmittingDiodeI, ArcI, FilamentI, GenericExcitationSourceI,
    DetectorI, FilterI,
    DichroicI,
)

from omero_acquisition_transfer.transfer.pack.common import convert_units


def export_instrument_metadata(instrument_obj: InstrumentI) -> Instrument:
    # Instrument
    id_: str = instrument_obj.getId()
    name: Optional[str] = instrument_obj.getName()

    # Microscope
    microscope_obj: MicroscopeI = instrument_obj.getMicroscope()
    microscope = export_microscope_metadata(microscope_obj)

    # Light source group
    light_sources_obj = instrument_obj.getLightSources()
    light_sources = export_light_sources_metadata(light_sources_obj)

    # Detectors
    detectors_obj = instrument_obj.getDetectors()
    detectors = export_detectors_metadata(detectors_obj)

    # Objectives
    objective_obj = instrument_obj.getObjective()
    objectives = export_objectives_metadata(objective_obj)

    # Filters
    filters_obj = instrument_obj.getFilters()
    filters = export_filters_metadata(filters_obj)

    # Dichroics
    dichroics_obj = instrument_obj.getDichroics()
    dichroics = export_dichroics_metadata(dichroics_obj)

    # Instrument
    instrument = Instrument(
        id=id_,
        name=name,
        microscope=microscope,
        light_source_group=light_sources,
        detectors=detectors,
        objectives=objectives,
        filters=filters,
        dichroics=dichroics,
    )

    return instrument


def export_microscope_metadata(microscope_obj: MicroscopeI) -> Optional[Microscope]:
    if microscope_obj is not None:
        id_: str = microscope_obj.getId()
        name: Optional[str] = microscope_obj.getName()
        manufacturer: Optional[str] = microscope_obj.getManufacturer()
        model: Optional[str] = microscope_obj.getModel()
        serial_number: Optional[str] = microscope_obj.getSerialNumber()
        lot_number: Optional[str] = microscope_obj.getLotNumber()

        type_: Optional[str] = None if not microscope_obj.getMicroscopeType() else microscope_obj.getMicroscopeType().getValue()

        microscope = Microscope(
            id=id_,
            name=name,
            manufacturer=manufacturer,
            model=model,
            serial_number=serial_number,
            lot_number=lot_number,
            type=type_,
        )

        return microscope
    return None


def export_light_sources_metadata(lss_obj: List) -> Optional[List[LightSource]]:
    if lss_obj:
        light_sources = []

        for ls_obj in lss_obj:
            light_source = export_light_source_metadata(ls_obj)

            if light_source:
                light_sources.append(light_source)

        return light_sources

    return []


def export_light_source_metadata(ls_obj) -> Optional[LightSource]:
    if isinstance(ls_obj._obj, LaserI):
        medium = None if not ls_obj.getLaserMedium() else ls_obj.getLaserMedium().getValue()
        if medium == 'Unknown':
            medium = None

        id_: int = ls_obj.getId()
        type_: Optional[str] = None if not ls_obj.getType() else ls_obj.getType().getValue()
        wavelength: Optional[float] = None if not ls_obj.getWavelength() else ls_obj.getWavelength().getValue()
        wavelength_unit: Optional[str] = None if not ls_obj.getWavelength() else ls_obj.getWavelength().getUnit()
        power: Optional[float] = None if not ls_obj.getPower() else ls_obj.getPower().getValue()
        power_unit: Optional[str] = None if not ls_obj.getPower() else ls_obj.getPower().getUnit()
        frequency_multiplication: Optional[int] = ls_obj.getFrequencyMultiplication()
        tunable: Optional[bool] = ls_obj.getTuneable()
        pockel_cell: Optional[bool] = ls_obj.getPockelCell()
        repetition_rate: Optional[float] = None if not ls_obj.getRepetitionRate() else ls_obj.getRepetitionRate().getValue()
        repetition_rate_unit: Optional[str] = None if not ls_obj.getRepetitionRate() else ls_obj.getRepetitionRate().getUnit()

        light_source = Laser(
            id=id_,
            type=type_,
            wavelength=wavelength,
            power=power,
            frequency_multiplication=frequency_multiplication,
            tunable=tunable,
            pockel_cell=pockel_cell,
            repetition_rate=repetition_rate,
            medium=medium,
        )

        if wavelength_unit:
            light_source.wavelength_unit = convert_units(wavelength_unit)
        if power_unit:
            light_source.power_unit = convert_units(power_unit)
        if repetition_rate_unit:
            light_source.repetition_rate_unit = convert_units(repetition_rate_unit)
    elif isinstance(ls_obj._obj, LightEmittingDiodeI):
        id_ = ls_obj.getId()
        power = None if not ls_obj.getPower() else ls_obj.getPower().getValue()
        power_unit = None if not ls_obj.getPower() else ls_obj.getPower().getUnit()

        light_source = LightEmittingDiode(
            id=id_,
            power=power,
        )

        if power_unit:
            light_source.power_unit = convert_units(power_unit)
    elif isinstance(ls_obj._obj, FilamentI):
        id_ = ls_obj.getId()
        power = None if not ls_obj.getPower() else ls_obj.getPower().getValue()
        power_unit = None if not ls_obj.getPower() else ls_obj.getPower().getUnit()

        light_source = Filament(
            id=id_,
            power=power,
        )

        if power_unit:
            light_source.power_unit = convert_units(power_unit)
    elif isinstance(ls_obj._obj, ArcI):
        id_ = ls_obj.getId()
        type_ = None if not ls_obj.getType() else ls_obj.getType().getValue()
        power = None if not ls_obj.getPower() else ls_obj.getPower().getValue()
        power_unit = None if not ls_obj.getPower() else ls_obj.getPower().getUnit()

        light_source = Arc(
            id=id_,
            type=type_,
            power=power,
        )

        if power_unit:
            light_source.power_unit = convert_units(power_unit)
    elif isinstance(ls_obj._obj, GenericExcitationSourceI):
        id_ = ls_obj.getId()
        power = None if not ls_obj.getPower() else ls_obj.getPower().getValue()
        power_unit = None if not ls_obj.getPower() else ls_obj.getPower().getUnit()

        light_source = GenericExcitationSource(
            id=id_,
            power=power,
        )

        if power_unit:
            light_source.power_unit = convert_units(power_unit)
    else:
        raise NotImplementedError(f'Light source type {type(ls_obj._obj)} not implemented')

    return light_source


def export_detectors_metadata(detectors_obj: List[DetectorI]) -> Optional[List[Detector]]:
    if detectors_obj:
        detectors = []

        for detector_obj in detectors_obj:
            detector = export_detector_metadata(detector_obj)

            if detector:
                detectors.append(detector)

        return detectors
    return []


def export_detector_metadata(detector_obj: DetectorI) -> Optional[Detector]:
    id_: int = detector_obj.getId()
    name: Optional[str] = detector_obj.getName()
    manufacturer: Optional[str] = detector_obj.getManufacturer()
    model: Optional[str] = detector_obj.getModel()
    serial_number: Optional[str] = detector_obj.getSerialNumber()
    type_: Optional[str] = None if not detector_obj.getType() else detector_obj.getType().getValue()
    lot_number: Optional[str] = detector_obj.getLotNumber()
    gain: Optional[float] = detector_obj.getGain()
    voltage: Optional[float] = None if not detector_obj.getVoltage() else detector_obj.getVoltage().getValue()
    voltage_unit: Optional[str] = None if not detector_obj.getVoltage() else detector_obj.getVoltage().getUnit()
    offset: Optional[float] = detector_obj.getOffsetValue()
    zoom: Optional[float] = detector_obj.getZoom()
    amplification_gain: Optional[float] = detector_obj.getAmplificationGain()

    if type_ == 'EM-CCD':
        type_ = 'EMCCD'

    detector = Detector(
        id=id_,
        name=name,
        manufacturer=manufacturer,
        model=model,
        type=type_,
        serial_number=serial_number,
        lot_number=lot_number,
        gain=gain,
        voltage=voltage,
        offset=offset,
        zoom=zoom,
        amplification_gain=amplification_gain,
    )

    if voltage_unit:
        detector.voltage_unit = convert_units(voltage_unit)

    return detector


def export_objectives_metadata(objectives_obj: List[ObjectiveI]) -> Optional[List[Objective]]:
    if objectives_obj:
        objectives = []

        for objective_obj in objectives_obj:
            objective = export_objective_metadata(objective_obj)
            if objective:
                objectives.append(objective)

        return objectives
    return []


def export_objective_metadata(objective_obj: ObjectiveI) -> Optional[Objective]:
    if objective_obj:
        id_: int = objective_obj.getId().getValue()
        manufacturer: Optional[str] = None if not objective_obj.getManufacturer() else objective_obj.getManufacturer().getValue()
        model: Optional[str] = None if not objective_obj.getModel() else objective_obj.getModel().getValue()
        serial_number: Optional[str] = None if not objective_obj.getSerialNumber() else objective_obj.getSerialNumber().getValue()
        lot_number: Optional[str] = None if not objective_obj.getLotNumber() else objective_obj.getLotNumber().getValue()
        correction: Optional[str] = None if not objective_obj.getCorrection().getValue() else objective_obj.getCorrection().getValue().getValue()
        immersion: Optional[str] = None if not objective_obj.getImmersion().getValue() else objective_obj.getImmersion().getValue().getValue()
        lens_na: Optional[float] = None if not objective_obj.getLensNA() else objective_obj.getLensNA().getValue()
        nominal_magnification: Optional[float] = None if not objective_obj.getNominalMagnification() else objective_obj.getNominalMagnification().getValue()
        calibrated_magnification: Optional[float] = None if not objective_obj.getCalibratedMagnification() else objective_obj.getCalibratedMagnification().getValue()
        working_distance: Optional[float] = None if not objective_obj.getWorkingDistance() else objective_obj.getWorkingDistance().getValue()
        working_distance_unit: Optional[str] = None if not objective_obj.getWorkingDistance() else objective_obj.getWorkingDistance().getUnit()
        iris: Optional[bool] = None if not objective_obj.getIris() else objective_obj.getIris().getValue()

        if correction == 'Unknown':
            correction = None
        if immersion == 'Unknown':
            immersion = None

        objective = Objective(
            id=id_,
            manufacturer=manufacturer,
            model=model,
            serial_number=serial_number,
            lot_number=lot_number,
            correction=correction,
            immersion=immersion,
            lens_na=lens_na,
            nominal_magnification=nominal_magnification,
            calibrated_magnification=calibrated_magnification,
            working_distance=working_distance,
            iris=iris,
        )

        if working_distance_unit:
            objective.working_distance_unit = convert_units(working_distance_unit)

        return objective
    return None


def export_filters_metadata(filters_obj: List[FilterI]) -> Optional[List[Filter]]:
    if filters_obj:
        filters = []

        for filter_obj in filters_obj:
            filter_ = export_filter_metadata(filter_obj)
            if filter_:
                filters.append(filter_)

        return filters
    return []


def export_filter_metadata(filter_obj: FilterI) -> Optional[Filter]:
    if filter_obj:
        id_: int = filter_obj.getId()
        manufacturer: Optional[str] = filter_obj.getManufacturer()
        model: Optional[str] = filter_obj.getModel()
        serial_number: Optional[str] = filter_obj.getSerialNumber()
        lot_number: Optional[str] = filter_obj.getLotNumber()
        type_: Optional[str] = None if not filter_obj.getType() else filter_obj.getType().getValue()
        filter_wheel: Optional[str] = filter_obj.getFilterWheel()

        filter_ = Filter(
            id=id_,
            manufacturer=manufacturer,
            model=model,
            serial_number=serial_number,
            lot_number=lot_number,
            type=type_,
            filter_wheel=filter_wheel,
        )

        if type_ == 'BandPass':
            tr_obj = filter_obj.getTransmittanceRange()
            if tr_obj is not None and tr_obj._obj is not None:
                cut_in: Optional[float] = None if not tr_obj.getCutIn() else tr_obj.getCutIn().getValue()
                cut_in_unit: Optional[str] = None if not tr_obj.getCutIn() else tr_obj.getCutIn().getUnit()
                cut_out: Optional[float] = None if not tr_obj.getCutOut() else tr_obj.getCutOut().getValue()
                cut_out_unit: Optional[str] = None if not tr_obj.getCutOut() else tr_obj.getCutOut().getUnit()

                range_ = TransmittanceRange(
                    cut_in=cut_in,
                    cut_out=cut_out,
                )

                if cut_in_unit:
                    range_.cut_in_unit = convert_units(cut_in_unit)
                if cut_out_unit:
                    range_.cut_out_unit = convert_units(cut_out_unit)

                filter_.transmittance_range = range_

        return filter_
    return None


def export_dichroics_metadata(dichroics_obj: List[DichroicI]) -> Optional[List[Dichroic]]:
    if dichroics_obj:
        dichroics = []

        for dichroic_obj in dichroics_obj:
            dichroic = export_dichroic_metadata(dichroic_obj)
            if dichroic:
                dichroics.append(dichroic)

        return dichroics
    return []


def export_dichroic_metadata(dichroic_obj: DichroicI) -> Optional[Dichroic]:
    if dichroic_obj:
        id_: int = dichroic_obj.getId()
        manufacturer: Optional[str] = dichroic_obj.getManufacturer()
        model: Optional[str] = dichroic_obj.getModel()
        serial_number: Optional[str] = dichroic_obj.getSerialNumber()
        lot_number: Optional[str] = dichroic_obj.getLotNumber()

        dichroic = Dichroic(
            id=id_,
            manufacturer=manufacturer,
            model=model,
            serial_number=serial_number,
            lot_number=lot_number,
        )

        return dichroic
    return None
