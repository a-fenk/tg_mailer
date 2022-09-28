import datetime
import logging
from time import sleep

from telethon.sync import TelegramClient
from telethon.tl.custom import Dialog
from progress.bar import Bar

import config
from config import TELEGRAM_SESSION_NAME, TELEGRAM_API_HASH, TELEGRAM_API_ID


logger = logging.getLogger(__name__)


def __reply(dialog: Dialog, message: str) -> None:
    if dialog.unread_count != 0:
        dialog.send_message(message)
        sleep(2)


def reply_to_unread_messages():
    with TelegramClient(
            TELEGRAM_SESSION_NAME,
            TELEGRAM_API_ID,
            TELEGRAM_API_HASH,
            request_retries=100,
            connection_retries=1000,
            retry_delay=10,
            timeout=10,
    ) as client:
        dialogs = client.get_dialogs()

        dialogs.sort(key=lambda obj: obj.unread_count)

        dialogs = client.get_dialogs(archived=False)

        target_dialogs = list(
            filter(
                lambda obj: obj.is_user and obj.unread_count > 0 and not list(client.iter_messages(obj.id, search=config.MESSAGE[1:50])),
                dialogs
            )
        )

        with Bar('Replying', max=len(target_dialogs)) as progress_bar:
            for dialog in target_dialogs:
                is_sent = False
                progress_bar.next()
                for attempt in range(10):
                    try:
                        __reply(dialog, config.MESSAGE)
                        client.send_read_acknowledge(dialog)
                        is_sent = True
                        break
                    except Exception as e:
                        print('\n')
                        logger.error(e)
                        logger.info(f'attempt {attempt+1}/10 failed')
                        sleep(30)
                if not is_sent:
                    logger.warning('failed to send a message, going to the next dialog.')


def mark_replied_as_readed():
    with TelegramClient(
            TELEGRAM_SESSION_NAME,
            TELEGRAM_API_ID,
            TELEGRAM_API_HASH,
            request_retries=100,
            connection_retries=1000,
            retry_delay=10,
            timeout=10,
    ) as client:
        my_id = client.get_me().id

        for obj in filter(
                lambda obj: obj.is_user and obj.unread_count > 0 and list(
                    client.iter_messages(obj.id, search=config.MESSAGE[1:50])
                ),
                client.get_dialogs(archived=False),
        ):
            if client.get_messages(obj)[0].get_sender().id == my_id:
                client.send_read_acknowledge(obj)
