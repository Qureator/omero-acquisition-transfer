# Copyright (c) 2023 Qureator, Inc. All rights reserved.

import omero
from getpass import getpass
from omero.gateway import BlitzGateway, ImageWrapper
from omero_voxel.ome import export_image_metadata
from ome_types import OME


def test_export_image_metadata(image: ImageWrapper, conn: BlitzGateway) -> OME:
    ome = OME()

    export_image_metadata(image, conn, ome, in_place=True)

    print(ome.to_xml())

    return ome


if __name__ == "__main__":
    client = omero.client(input("Host: "), 4064)
    client.createSession(input("Username: "), getpass("Password: "))
    client.enableKeepAlive(60)

    try:
        conn = BlitzGateway(client_obj=client)
        conn.SERVICE_OPTS.setOmeroGroup(str(input("Group ID: ")))

        image = conn.getObject("Image", int(input("Image ID: ")))
        ome = test_export_image_metadata(image, conn)
    finally:
        client.closeSession()
