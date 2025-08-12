from __future__ import annotations
import logging
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from neonize.aioze.client import NewAClient
    from neonize.aioze.events import MessageEv

class SerializedMessage:
    def __init__(self, client: NewAClient, event: MessageEv):
        self.client = client
        self.event = event
        self._quoted = None

    @property
    def chat(self) -> str:
        """The JID of the chat where the message was sent."""
        return self.event.info.message_source.chat.jid

    @property
    def sender(self) -> str:
        """The JID of the user who sent the message."""
        return self.event.info.message_source.sender.jid

    @property
    def isGroup(self) -> bool:
        """Whether the message was sent in a group."""
        return self.chat.endswith('@g.us')

    @property
    def text(self) -> str:
        """The text content of the message."""
        return self.event.message.conversation or ""

    @property
    def quoted(self) -> Optional[SerializedMessage]:
        """The quoted message, if any."""
        # This is a simplified implementation. A full implementation would
        # need to fetch the full quoted message details from the store if not present.
        if self._quoted:
            return self._quoted

        context_info = self.event.message.extended_text_message.context_info if self.event.message.extended_text_message else None
        if not context_info or not context_info.quoted_message:
            return None

        # This is a mock-up. `neonize` doesn't directly provide the full event for the quoted message.
        # A real implementation would require more work, possibly fetching the message from a store.
        # For now, we create a new "dummy" event to wrap.
        # This part will need to be improved later.
        logging.warning("Quoted message serialization is currently a simplified mock-up.")

        # We don't have the full event, so we can't fully serialize the quoted message yet.
        # This is a placeholder for future development.
        return None

    def reply(self, text: str):
        """A simple method to reply to the current message."""
        return self.client.reply_message(text, self.event.message)
