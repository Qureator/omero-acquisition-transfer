import os
import string
import tifftools
from typing import List, Optional
from ome_types import OME, to_dict, to_xml
from ome_types.model import InstrumentRef
from omero.gateway import BlitzGateway, ImageWrapper
from pathlib import Path

from .exports import (
    export_instrument_metadata,
    export_pixels_metadata,
    export_imaging_environment_metadata,
    export_objective_settings_metadata,
)

__all__ = ["merge_metadata_tiff", "move_tiff_files"]


def merge_metadata_tiff(image: ImageWrapper, tiff_path: str) -> None:
    """Merge metadata from image to tiff file.

    Parameters
    ----------
    image : omero.gateway.ImageWrapper
        Image to get metadata from.
    tiff_path : str
        File name of tiff file.
    """
    # Get metadata from image
    instrument = export_instrument_metadata(image.getInstrument())
    pixels = export_pixels_metadata(image)
    imaging_environment = export_imaging_environment_metadata(image.getImagingEnvironment())
    objective_settings = export_objective_settings_metadata(image.getObjectiveSettings())

    # Read tifffile
    tiff = tifftools.read_tiff(tiff_path)

    # Merge metadata to ome object
    ome = OME(**to_dict(tiff['ifds'][0]['tags'][tifftools.Tag.ImageDescription.value]['data'], parser='lxml'))

    ome.instruments.append(instrument)
    ome.images[0].instrument_ref = InstrumentRef(id=ome.instruments[-1].id)
    ome.images[0].pixels.channels = pixels.channels
    ome.images[0].objective_settings = objective_settings
    ome.images[0].imaging_environment = imaging_environment

    # Write tifffile
    tiff["ifds"][0]["tags"][tifftools.Tag.ImageDescription.value]["data"] = to_xml(ome)

    # Wierd bug: not properly write tiff file if the file is existing even if it is removed or
    tifftools.write_tiff(tiff, tiff_path.replace(".tiff", "_new.tiff"))
    os.remove(tiff_path)
    os.rename(tiff_path.replace(".tiff", "_new.tiff"), tiff_path)


def move_tiff_files(
    conn: BlitzGateway,
    target_type: str,
    target_ids: List[int],
    tiff_paths: List[str],
    folder: str,
) -> List[str]:
    """Move tiff files by their screen/plate/dataset/project folder structure.

    Parameters
    ----------
    conn : omero.gateway.BlitzGateway
        OMERO connection.

    target_type : str
        Data type of the data ID.
        e.g. 'Screen', 'Plate', 'Project', 'Dataset', 'Image'

    target_ids : List[int]
        Data IDs to construct folder structure for tiff files.

    tiff_paths : list [str]
        List of tiff file paths.
        The name should be constructed their image ID.
        e.g. pixel_datas/100001.tiff, pixel_datas/100002.tiff, ...

    folder : str
        Folder name to save tiff files.
    """

    if target_type not in {"Screen", "Plate", "Dataset", "Project", "Image"}:
        raise ValueError("Data type not supported.")

    # Get sorted tiff paths by their data type
    if target_type == "Screen":
        tiff_paths_sorted = rename_tiff_paths_by_screen(conn, target_ids)
    elif target_type == "Plate":
        tiff_paths_sorted = rename_tiff_paths_by_plate(conn, target_ids)
    elif target_type == "Dataset":
        tiff_paths_sorted = rename_tiff_paths_by_dataset(conn, target_ids)
    elif target_type == "Project":
        tiff_paths_sorted = rename_tiff_paths_by_project(conn, target_ids)
    elif target_type == "Image":
        tiff_paths_sorted = rename_tiff_paths_by_image(conn, target_ids, add_name=True)
    else:
        raise ValueError("Data type not supported.")

    tiff_paths_sorted = [os.path.join("pixel_images", path) for path in tiff_paths_sorted]
    tiff_paths_sorted.sort(key=lambda x: Path(x).stem.split("-")[-1])

    # Move tiff files with sorted tiff paths
    for source_path, dest_path in zip(tiff_paths, tiff_paths_sorted):
        dest_path = os.path.join(folder, dest_path)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        os.rename(source_path, dest_path)

    return tiff_paths_sorted


def rename_tiff_paths_by_screen(conn: BlitzGateway, screen_ids: List[int]) -> List[str]:
    """Rename tiff paths by their screen/plate/dataset/project folder structure.

    Parameters
    ----------
    conn : omero.gateway.BlitzGateway
        OMERO connection.

    screen_ids : List[int]
        Screen IDs to construct folder structure for tiff files.

    tiff_paths : list [str]
        List of tiff file paths.
        The name should be constructed their image ID.
        e.g. pixel_datas/100001.tiff, pixel_datas/100002.tiff, ...

    Returns
    -------
    tiff_paths_sorted : list [str]
        List of sorted tiff file paths.
    """
    tiff_paths_map = {}
    plate_ids = []
    for screen_id in screen_ids:
        screen = conn.getObject("Screen", screen_id)
        for plate in screen.listChildren():
            plate_ids.append(plate.getId())
            tiff_paths_map[plate.getId()] = "Screen-" + str(screen_id)

    tiff_paths_sorted = [rename_tiff_paths_by_plate(conn, [plate_id]) for plate_id in plate_ids]
    tiff_paths_sorted = [
        os.path.join(tiff_paths_map[plate_id], value)
        for plate_id, values in zip(plate_ids, tiff_paths_sorted)
        for value in values
    ]

    return tiff_paths_sorted


def rename_tiff_paths_by_plate(conn: BlitzGateway, plate_ids: List[int]) -> List[str]:
    """Rename tiff paths by their screen/plate/dataset/project folder structure.

    Parameters
    ----------
    conn : omero.gateway.BlitzGateway
        OMERO connection.

    plate_ids : List[int]
        Plate IDs to construct folder structure for tiff files.

    tiff_paths : list [str]
        List of tiff file paths.
        The name should be constructed their image ID.
        e.g. pixel_images/100001.tiff, pixel_images/100002.tiff, ...

    Returns
    -------
    tiff_paths_sorted : list [str]
        List of sorted tiff file paths.
    """
    tiff_paths_map = {}
    image_ids = []
    for plate_id in plate_ids:
        plate = conn.getObject("Plate", plate_id)
        for well in plate.listChildren():
            for ws in well.listChildren():
                image = ws.image()
                image_ids.append(image.getId())
                tiff_paths_map[image.getId()] = os.path.join(
                    "Plate-" + str(plate_id), well.getWellPos() + "-"
                )

    tiff_paths_sorted = rename_tiff_paths_by_image(conn, image_ids)
    tiff_paths_sorted = [
        tiff_paths_map[image_id] + value for image_id, value in zip(image_ids, tiff_paths_sorted)
    ]

    return tiff_paths_sorted


def rename_tiff_paths_by_dataset(conn: BlitzGateway, dataset_ids: List[int]) -> List[str]:
    """Sort tiff paths by their screen/plate/dataset/project folder structure.

    Parameters
    ----------
    conn : omero.gateway.BlitzGateway
        OMERO connection.

    dataset_ids : List[int]
        Dataset IDs to construct folder structure for tiff files.

    tiff_paths : list [str]
        List of tiff file paths.
        The name should be constructed their image ID.
        e.g. pixel_datas/100001.tiff, pixel_datas/100002.tiff, ...

    Returns
    -------
    tiff_paths_sorted : list [str]
        List of sorted tiff file paths.
    """
    tiff_paths_map = {}
    image_ids = []
    for dataset_id in dataset_ids:
        dataset = conn.getObject("Dataset", dataset_id)
        for image in dataset.listChildren():
            image_ids.append(image.getId())
            tiff_paths_map[image.getId()] = "Dataset-" + str(dataset.getId())

    tiff_paths_sorted = rename_tiff_paths_by_image(conn, image_ids, add_name=True)
    tiff_paths_sorted = [
        os.path.join(tiff_paths_map[image_id], value)
        for image_id, value in zip(image_ids, tiff_paths_sorted)
    ]

    return tiff_paths_sorted


def rename_tiff_paths_by_project(conn: BlitzGateway, project_ids: List[int]) -> List[str]:
    """Sort tiff paths by their screen/plate/dataset/project folder structure.

    Parameters
    ----------
    conn : omero.gateway.BlitzGateway
        OMERO connection.

    project_ids : List[int]
        Project IDs to construct folder structure for tiff files.

    tiff_paths : list [str]
        List of tiff file paths.
        The name should be constructed their image ID.
        e.g. pixel_datas/100001.tiff, pixel_datas/100002.tiff, ...

    Returns
    -------
    tiff_paths_sorted : list [str]
        List of sorted tiff file paths.
    """
    tiff_paths_map = {}
    dataset_ids = []
    for project_id in project_ids:
        project = conn.getObject("Project", project_id)
        for dataset in project.listChildren():
            dataset_ids.append(dataset.getId())
            tiff_paths_map[dataset.getId()] = "Project-" + str(project.getId())

    tiff_paths_sorted = [
        rename_tiff_paths_by_dataset(conn, dataset_id) for dataset_id in dataset_ids
    ]
    tiff_paths_sorted = [
        os.path.join(tiff_paths_map[dataset_id], value)
        for dataset_id, values in zip(dataset_ids, tiff_paths_sorted)
        for value in values
    ]

    return tiff_paths_sorted


def rename_tiff_paths_by_image(
    conn: BlitzGateway, image_ids: List[int], add_name: bool = False
) -> List[str]:
    """Sort tiff paths by their screen/plate/dataset/project folder structure.

    Parameters
    ----------
    conn : omero.gateway.BlitzGateway
        OMERO connection.

    image_ids : List[int]
        Image IDs to construct folder structure for tiff files.

    tiff_paths : list [str]
        List of tiff file paths.
        The name should be constructed their image ID.
        e.g. pixel_datas/100001.tiff, pixel_datas/100002.tiff, ...

    add_name : bool
        Add image name to the tiff path.

    Returns
    -------
    tiff_paths_sorted : list [str]
        List of sorted tiff file paths.
    """

    def clean_name(name: str, valid_chars: Optional[str] = None) -> str:
        if valid_chars is None:
            valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)

        cleaned_name = "".join(c for c in name if c in valid_chars)
        return cleaned_name

    tiff_paths_sorted = []
    for image_id in image_ids:
        image = conn.getObject("Image", image_id)
        if add_name:
            cleaned_name = clean_name(image.getName())
            tiff_paths_sorted.append(f"{cleaned_name}-{image.getId()}.tiff")
        else:
            tiff_paths_sorted.append(f"{image.getId()}.tiff")

    return tiff_paths_sorted
