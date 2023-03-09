# Copyright (c) 2023 Qureator, Inc. All rights reserved.

from typing import List, Dict, Any, Union

from ome_types.model import (
    Instrument,
    Microscope,
    Detector,
    LightSource, Laser, Arc, Filament, LightEmittingDiode, GenericExcitationSource,
    Objective,
    Filter, TransmittanceRange,
    Dichroic,
)
from omero.gateway import BlitzGateway
from omero.model import (
    InstrumentI,
    MicroscopeI,
    DetectorI,
    LaserI, ArcI, FilamentI, LightEmittingDiodeI, GenericExcitationSourceI,
    ObjectiveI,
    FilterI, TransmittanceRangeI,
    DichroicI,
)

from .common import update_metadata, update_length_metadata, update_enum_metadata


def create_instruments(instruments: List[Instrument], conn: BlitzGateway) -> Dict[str, Any]:
    omero_id_to_objects = {}

    for instrument in instruments:
        omero_id_to_objects.update(create_instrument(instrument, conn))

    return omero_id_to_objects


def create_instrument(instrument: Instrument, conn: BlitzGateway) -> Dict[str, Any]:
    instrument_obj = InstrumentI()

    # Microscope
    omero_id_to_objects, instrument_obj = create_microscope(instrument.microscope, instrument_obj, conn)

    # Light source
    res, instrument_obj = create_light_sources(instrument.light_source_group, instrument_obj, conn)
    omero_id_to_objects.update(res)

    # Detector
    res, instrument_obj = create_detectors(instrument.detectors, instrument_obj, conn)
    omero_id_to_objects.update(res)

    # Objective
    res, instrument_obj = create_objectives(instrument.objectives, instrument_obj, conn)
    omero_id_to_objects.update(res)

    # Filter
    res, instrument_obj = create_filters(instrument.filters, instrument_obj, conn)
    omero_id_to_objects.update(res)

    # Dichroic
    res, instrument_obj = create_dichroics(instrument.dichroics, instrument_obj, conn)
    omero_id_to_objects.update(res)

    instrument_obj = conn.getUpdateService().saveAndReturnObject(instrument_obj, conn.SERVICE_OPTS)
    omero_id_to_objects[instrument.id] = instrument_obj

    return omero_id_to_objects


def create_microscope(
        microscope: Microscope, instrument_obj: InstrumentI, conn: BlitzGateway
) -> Union[Dict[str, Any], InstrumentI]:

    if microscope is None:
        return {}

    if instrument_obj.getMicroscope() is not None:
        return {}

    microscope_obj = MicroscopeI()

    update_metadata(microscope_obj, 'manufacturer', microscope.manufacturer)
    update_metadata(microscope_obj, 'model', microscope.model)
    update_metadata(microscope_obj, 'serialNumber', microscope.serial_number)
    update_metadata(microscope_obj, 'lotNumber', microscope.lot_number)
    update_enum_metadata(microscope_obj, 'type', microscope.type, 'MicroscopeTypeI', conn)

    microscope_obj = conn.getUpdateService().saveAndReturnObject(microscope_obj, conn.SERVICE_OPTS)

    instrument_obj = InstrumentI(instrument_obj.id)
    instrument_obj.setMicroscope(microscope_obj)
    instrument_obj = conn.getUpdateService().saveAndReturnObject(instrument_obj, conn.SERVICE_OPTS)

    # A Microscope doesn't have an ID
    return {}, instrument_obj


def create_light_sources(
        light_sources: List[LightSource], instrument_obj: InstrumentI, conn: BlitzGateway
) -> Union[Dict[str, Any], InstrumentI]:
    omero_id_to_obj = {}

    for light_source in light_sources:
        res = create_light_source(light_source, instrument_obj, conn)
        omero_id_to_obj.update(res)

        instrument_obj.addLightSource(res[light_source.id])

    instrument_obj = conn.getUpdateService().saveAndReturnObject(instrument_obj, conn.SERVICE_OPTS)

    return omero_id_to_obj, instrument_obj


def create_light_source(
        light_source: LightSource, instrument_obj: InstrumentI, conn: BlitzGateway
) -> Dict[str, Any]:
    if isinstance(light_source, Laser):
        light_source_obj = LaserI()

        medium_str = light_source.laser_medium
        if medium_str is None:
            medium_str = 'Unknown'

        update_enum_metadata(light_source_obj, 'type', light_source.type, 'LaserTypeI', conn)
        update_enum_metadata(light_source_obj, 'laserMedium', medium_str, 'LaserMediumI', conn)
        update_length_metadata(light_source_obj, 'wavelength', light_source.wavelength, light_source.wavelength_unit)
        update_metadata(light_source_obj, 'frequencyMultiplication', light_source.frequency_multiplication)
        update_metadata(light_source_obj, 'tuneable', light_source.tuneable)
        update_metadata(light_source_obj, 'pulse', light_source.pulse)
        update_metadata(light_source_obj, 'pockelCell', light_source.pockel_cell)
        update_length_metadata(light_source_obj,
                               'repetitionRate',
                               light_source.repetition_rate,
                               light_source.repetition_rate_unit)
    elif isinstance(light_source, Arc):
        light_source_obj = ArcI()
        update_enum_metadata(light_source_obj, 'type', light_source.type, 'ArcTypeI', conn)
    elif isinstance(light_source, LightEmittingDiode):
        light_source_obj = LightEmittingDiodeI()
    elif isinstance(light_source, Filament):
        light_source_obj = FilamentI()
        update_enum_metadata(light_source_obj, 'type', light_source.type, 'FilamentTypeI', conn)
    elif isinstance(light_source, GenericExcitationSource):
        light_source_obj = GenericExcitationSourceI()
    else:
        raise Exception(f'Unknown light source type: {type(light_source)}')

    light_source_obj.setInstrument(instrument_obj)

    update_metadata(light_source_obj, 'manufacturer', light_source.manufacturer)
    update_metadata(light_source_obj, 'model', light_source.model)
    update_metadata(light_source_obj, 'serialNumber', light_source.serial_number)
    update_metadata(light_source_obj, 'lotNumber', light_source.lot_number)

    update_length_metadata(light_source_obj, 'power', light_source.power, light_source.power_unit)

    light_source_obj = conn.getUpdateService().saveAndReturnObject(light_source_obj, conn.SERVICE_OPTS)

    return {light_source.id: light_source_obj}


def create_detectors(
        detectors: List[Detector], instrument_obj: InstrumentI, conn: BlitzGateway
) -> Union[Dict[str, DetectorI], InstrumentI]:
    omero_id_to_obj = {}
    instrument_obj = conn.getMetadataService().loadInstrument(instrument_obj.id.val, conn.SERVICE_OPTS)

    for detector in detectors:
        res = create_detector(detector, instrument_obj, conn)
        omero_id_to_obj.update(res)

        instrument_obj.addDetector(res[detector.id])
    instrument_obj = conn.getUpdateService().saveAndReturnObject(instrument_obj, conn.SERVICE_OPTS)

    return omero_id_to_obj, instrument_obj


def create_detector(
        detector: Detector, instrument_obj: InstrumentI, conn: BlitzGateway
) -> Dict[str, DetectorI]:
    detector_obj = DetectorI()
    detector_obj.setInstrument(instrument_obj)

    type_ = detector.type

    if type_.value == 'EMCCD':
        type_ = 'EM-CCD'

    update_metadata(detector_obj, 'manufacturer', detector.manufacturer)
    update_metadata(detector_obj, 'model', detector.model)
    update_metadata(detector_obj, 'serialNumber', detector.serial_number)
    update_metadata(detector_obj, 'lotNumber', detector.lot_number)
    update_enum_metadata(detector_obj, 'type', type_, 'DetectorTypeI', conn)
    update_metadata(detector_obj, 'gain', detector.gain)
    update_length_metadata(detector_obj, 'voltage', detector.voltage, detector.voltage_unit)
    update_metadata(detector_obj, 'offsetValue', detector.offset)
    update_metadata(detector_obj, 'zoom', detector.zoom)
    update_metadata(detector_obj, 'amplificationGain', detector.amplification_gain)

    detector_obj = conn.getUpdateService().saveAndReturnObject(detector_obj, conn.SERVICE_OPTS)

    return {detector.id: detector_obj}


def create_objectives(
        objectives: List[Objective], instrument_obj: InstrumentI, conn: BlitzGateway
) -> Union[Dict[str, ObjectiveI], InstrumentI]:
    omero_id_to_obj = {}
    instrument_obj = conn.getMetadataService().loadInstrument(instrument_obj.id.val, conn.SERVICE_OPTS)

    for objective in objectives:
        res = create_objective(objective, instrument_obj, conn)
        omero_id_to_obj.update(res)

        instrument_obj.addObjective(res[objective.id])
    instrument_obj = conn.getUpdateService().saveAndReturnObject(instrument_obj, conn.SERVICE_OPTS)

    return omero_id_to_obj, instrument_obj


def create_objective(
        objective: Objective, instrument_obj: InstrumentI, conn: BlitzGateway
) -> Dict[str, ObjectiveI]:
    objective_obj = ObjectiveI()
    objective_obj.setInstrument(instrument_obj)

    correction = objective.correction if objective.correction is not None else 'Unknown'
    immersion = objective.immersion if objective.immersion is not None else 'Unknown'

    update_metadata(objective_obj, 'manufacturer', objective.manufacturer)
    update_metadata(objective_obj, 'model', objective.model)
    update_metadata(objective_obj, 'serialNumber', objective.serial_number)
    update_metadata(objective_obj, 'lotNumber', objective.lot_number)
    update_enum_metadata(objective_obj, 'correction', correction, 'CorrectionI', conn)
    update_enum_metadata(objective_obj, 'immersion', immersion, 'ImmersionI', conn)
    update_metadata(objective_obj, 'lensNA', objective.lens_na)
    update_metadata(objective_obj, 'nominalMagnification', objective.nominal_magnification)
    update_metadata(objective_obj, 'calibratedMagnification', objective.calibrated_magnification)
    update_length_metadata(objective_obj, 'workingDistance', objective.working_distance, objective.working_distance_unit)
    update_metadata(objective_obj, 'iris', objective.iris)

    objective_obj = conn.getUpdateService().saveAndReturnObject(objective_obj, conn.SERVICE_OPTS)

    return {objective.id: objective_obj}


def create_filters(
        filters: List[Filter], instrument_obj: InstrumentI, conn: BlitzGateway
) -> Union[Dict[str, FilterI], InstrumentI]:
    omero_id_to_obj = {}
    instrument_obj = conn.getMetadataService().loadInstrument(instrument_obj.id.val, conn.SERVICE_OPTS)

    for filter_ in filters:
        res = create_filter(filter_, instrument_obj, conn)
        omero_id_to_obj.update(res)

        instrument_obj.addFilter(res[filter_.id])
    instrument_obj = conn.getUpdateService().saveAndReturnObject(instrument_obj, conn.SERVICE_OPTS)

    return omero_id_to_obj, instrument_obj


def create_filter(
        filter_: Filter, instrument_obj: InstrumentI, conn: BlitzGateway
) -> Dict[str, FilterI]:
    filter_obj = FilterI()

    update_metadata(filter_obj, 'manufacturer', filter_.manufacturer)
    update_metadata(filter_obj, 'model', filter_.model)
    update_metadata(filter_obj, 'serialNumber', filter_.serial_number)
    update_metadata(filter_obj, 'lotNumber', filter_.lot_number)

    update_enum_metadata(filter_obj, 'type', filter_.type, 'FilterTypeI', conn)
    update_metadata(filter_obj, 'filterWheel', filter_.filter_wheel)

    filter_obj.setInstrument(instrument_obj)

    if filter_.type.value == 'BandPass':
        tr_range_obj = TransmittanceRangeI()
        tr_range: TransmittanceRange = filter_.transmittance_range
        update_length_metadata(tr_range_obj, 'cutIn', tr_range.cut_in, tr_range.cut_in_unit)
        update_length_metadata(tr_range_obj, 'cutOut', tr_range.cut_out, tr_range.cut_out_unit)

        filter_obj.setTransmittanceRange(tr_range_obj)

    filter_obj = conn.getUpdateService().saveAndReturnObject(filter_obj, conn.SERVICE_OPTS)
    return {filter_.id: filter_obj}


def create_dichroics(
        dichroics: List[Dichroic], instrument_obj: InstrumentI, conn: BlitzGateway
) -> Union[Dict[str, DichroicI], InstrumentI]:
    omero_id_to_obj = {}
    instrument_obj = conn.getMetadataService().loadInstrument(instrument_obj.id.val, conn.SERVICE_OPTS)

    for dichroic in dichroics:
        res = create_dichroic(dichroic, instrument_obj, conn)
        omero_id_to_obj.update(res)

        instrument_obj.addDichroic(res[dichroic.id])
    instrument_obj = conn.getUpdateService().saveAndReturnObject(instrument_obj, conn.SERVICE_OPTS)

    return omero_id_to_obj, instrument_obj


def create_dichroic(
        dichroic: Dichroic, instrument_obj: InstrumentI, conn: BlitzGateway
) -> Dict[str, DichroicI]:
    dichroic_obj = DichroicI()

    update_metadata(dichroic_obj, 'manufacturer', dichroic.manufacturer)
    update_metadata(dichroic_obj, 'model', dichroic.model)
    update_metadata(dichroic_obj, 'serialNumber', dichroic.serial_number)
    update_metadata(dichroic_obj, 'lotNumber', dichroic.lot_number)

    dichroic_obj.setInstrument(instrument_obj)

    dichroic_obj = conn.getUpdateService().saveAndReturnObject(dichroic_obj, conn.SERVICE_OPTS)

    return {dichroic.id: dichroic_obj}
