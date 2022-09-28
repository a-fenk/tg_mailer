import datetime
from time import sleep

from telethon.sync import TelegramClient
from telethon.tl.custom import Dialog
from progress.bar import Bar

import config
from config import TELEGRAM_SESSION_NAME, TELEGRAM_API_HASH, TELEGRAM_API_ID


def __reply(dialog: Dialog, message: str) -> None:
    if dialog.unread_count != 0:
        try:
            dialog.send_message(message)
            sleep(2)
        except Exception as e:
            sleep(60)
            __reply(dialog, message)


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
        with open('replied_dialogs.txt', 'r') as f:
            ids_string = f.read()
            replied_dialogs = list(map(int, ids_string.split('\n') if ids_string else []))

        dialogs = client.get_dialogs()

        dialogs.sort(key=lambda obj: obj.unread_count)

        dialogs = client.get_dialogs(archived=False)
        dialogs.sort(key=lambda dialog: dialog.unread_count)

        unread_dialogs = list(
            filter(
                lambda obj: obj.is_user and obj.unread_count > 0 and obj.id not in replied_dialogs, dialogs
            )
        )

        try:
            with Bar('Replying', max=len(unread_dialogs)) as progress_bar:
                for dialog in unread_dialogs:
                    print(datetime.datetime.now())
                    progress_bar.next()
                    __reply(dialog, config.MESSAGE)
                    replied_dialogs.append(dialog.id)
        except Exception as e:
            pass

        with open('replied_dialogs.txt', 'w') as f:
            f.write('\n'.join(list(map(str, replied_dialogs))))
