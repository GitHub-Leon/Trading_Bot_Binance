from win10toast_click import ToastNotifier

from src.config import DESKTOP_NOTIFICATIONS
from src.helpers.scripts.logger import debug_log


def desktop_notify(title, message, click_callback_func):
    debug_log(f'Create a desktop notification {title}. Call-back-function: {callable(click_callback_func)}', False)

    if not DESKTOP_NOTIFICATIONS:
        debug_log("User does not want to get a desktop notification", False)
        return False
    notification = ToastNotifier()

    notification.show_toast(
        title,  # title
        message,  # message
        icon_path="./img/icon.ico",  # 'icon_path'
        duration=10,  # for how many seconds toast should be visible; None = leave notification in Notification Center
        threaded=True,
        # True = run other code in parallel; False = code execution will wait till notification disappears
        callback_on_click=click_callback_func  # click notification to run function
    )
    return True
