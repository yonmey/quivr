from enum import Enum
from typing import List, Union
from uuid import UUID

from modules.notification.entity.notification import Notification
from modules.notification.service.notification_service import NotificationService
from packages.utils import parse_message_time
from pydantic import BaseModel
from repository.chat.get_chat_history import GetChatHistoryOutput, get_chat_history


class ChatItemType(Enum):
    MESSAGE = "MESSAGE"
    NOTIFICATION = "NOTIFICATION"


class ChatItem(BaseModel):
    item_type: ChatItemType
    body: Union[GetChatHistoryOutput, Notification]


notification_service = NotificationService()


# Move these methods to ChatService in chat module
def merge_chat_history_and_notifications(
    chat_history: List[GetChatHistoryOutput], notifications: List[Notification]
) -> List[ChatItem]:
    chat_history_and_notifications = chat_history + notifications

    chat_history_and_notifications.sort(
        key=lambda x: parse_message_time(x.message_time)
        if isinstance(x, GetChatHistoryOutput)
        else parse_message_time(x.datetime)
    )

    transformed_data = []
    for item in chat_history_and_notifications:
        if isinstance(item, GetChatHistoryOutput):
            item_type = ChatItemType.MESSAGE
            body = item
        else:
            item_type = ChatItemType.NOTIFICATION
            body = item
        transformed_item = ChatItem(item_type=item_type, body=body)
        transformed_data.append(transformed_item)

    return transformed_data


def get_chat_history_with_notifications(
    chat_id: UUID,
) -> List[ChatItem]:
    chat_history = get_chat_history(str(chat_id))
    chat_notifications = notification_service.get_chat_notifications(chat_id)
    return merge_chat_history_and_notifications(chat_history, chat_notifications)
