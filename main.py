"""
Example for a BLE 4.0 Server
"""

import logging
import asyncio

from typing import Any

from bless import (  # type: ignore
    BlessServer,
    BlessGATTCharacteristic,
    GATTCharacteristicProperties,
    GATTAttributePermissions,
)

my_service_name = "Test Service"
my_service_uuid = "A07498CA-AD5B-474E-940D-16F1FBE7E8CD"
my_char_uuid = "51FF12BB-3ED8-46E5-B4F9-D64E2FEC021B"
server = None

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(name=__name__)


def read_request(characteristic: BlessGATTCharacteristic) -> bytearray:
    logger.debug(f"Reading {characteristic.value}")
    return characteristic.value


def write_request(characteristic: BlessGATTCharacteristic, value: Any):
    characteristic.value = value

    # Notify subscribers
    # TODO: Process commands and response data
    server.update_value(my_service_uuid, my_char_uuid)


def notify(server, value):
    server.get_characteristic(
        my_char_uuid,
    ).value = value
    server.update_value(my_service_uuid, my_char_uuid)


async def run(loop):
    # Instantiate the server
    global server
    server = BlessServer(name=my_service_name, loop=loop)
    server.read_request_func = read_request
    server.write_request_func = write_request

    # Add Service
    await server.add_new_service(my_service_uuid)

    # Add a Characteristic to the service
    char_flags = (
        GATTCharacteristicProperties.read
        | GATTCharacteristicProperties.write
        | GATTCharacteristicProperties.indicate
    )
    permissions = GATTAttributePermissions.readable | GATTAttributePermissions.writeable
    await server.add_new_characteristic(
        my_service_uuid, my_char_uuid, char_flags, None, permissions
    )

    # Start BLE Server
    await server.start()

    logger.debug("Waiting for someone to subscribe")
    while not await server.is_connected():
        await asyncio.sleep(0.1)

    logger.debug("New subscription.")
    notify(server, b"Welcome")

    # Console interaction inside server
    while True:
        a = input("Value: ")
        if a == "quit":
            break
        else:
            notify(server, a.encode())
        await asyncio.sleep(0.5)

    logger.debug("Stopping server")
    await server.stop()


loop = asyncio.get_event_loop()

try:
    loop.run_until_complete(run(loop))
finally:
    loop.close()
