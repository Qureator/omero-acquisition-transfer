import omero
from getpass import getpass
from omero.gateway import BlitzGateway, ImageWrapper
from omero_voxel.ome import export_image_metadata
from omero_voxel.ome import attach_image_metadata, create_instruments
from ome_types import OME


def test_export_image_metadata(image: ImageWrapper, conn: BlitzGateway) -> OME:
    ome = OME()
    export_image_metadata(image, conn, ome, in_place=True)
    print(ome.to_xml())

    return ome


def test_attach_image_metadata(image: ImageWrapper, conn: BlitzGateway, ome: OME) -> None:
    omero_id_to_object = create_instruments(ome.instruments, conn)

    if ome.images[0].instrument_ref is not None:
        image.setInstrument(omero_id_to_object[ome.images[0].instrument_ref.id])

    image.save()

    attach_image_metadata(ome.images[0], image, omero_id_to_object, conn)


if __name__ == "__main__":
    client = omero.client(input("Host: "), 4064)
    client.createSession(input("Username: "), getpass("Password: "))
    client.enableKeepAlive(60)

    try:
        conn = BlitzGateway(client_obj=client)
        conn.SERVICE_OPTS.setOmeroGroup(str(input("Group ID: ")))

        image = conn.getObject("Image", int(input("From Image ID: ")))
        ome = test_export_image_metadata(image, conn)

        image = conn.getObject("Image", int(input("To Image ID: ")))
        test_attach_image_metadata(image, conn, ome)
    finally:
        client.closeSession()
