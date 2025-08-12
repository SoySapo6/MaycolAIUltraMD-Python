from .message import SerializedMessage
from neonize.aioze.client import NewAClient
from neonize.aioze.events import MessageEv

def serialize_message(client: NewAClient, event: MessageEv) -> SerializedMessage:
    """
    Serializes a raw message event into a more convenient object.
    """
    return SerializedMessage(client, event)
