__id__ = "status_adder"
__name__ = "Status Adder"
__description__ = "Позволяет добавлять кастомные статусы в стиле Discord в качестве имени и быстро переключаться между ними. \n\nСсылка на документацию в настройках плагина!"
__author__ = "@itNotMax - @MaxExteraPlugins"
__version__ = "1.9.0"
__icon__ = "MaxExteraPluginsStickers/16"
__min_version__ = "12.10.6"
__app_version__ = ">=12.5.1"
__sdk_version__ = ">=1.4.3.3"

from base_plugin import BasePlugin, AppEvent, MenuItemData, MenuItemType
from android_utils import run_on_ui_thread, OnClickListener, log
from client_utils import (
    get_user_config,
    get_messages_controller,
    get_notification_center,
    get_connections_manager,
    get_last_fragment,
)
from ui.bulletin import BulletinHelper
from ui.alert import AlertDialogBuilder
from ui.settings import Header, Input, Divider, Text, Switch
from hook_utils import find_class, get_private_field
from java import jclass
from java.lang import Long as JLong, Integer as JInteger
from typing import List, Any, Dict
import json

DEFAULT_TEMPLATES = [
    {"emoji": "🌐", "caption": ""},
    {"emoji": "🟢", "caption": "[online]"},
    {"emoji": "🔴", "caption": "[busy]"},
    {"emoji": "🌙", "caption": "[afk]"},
    {"emoji": "🎯", "caption": ""},
]
DEFAULT_FORMAT = "{status} {name}"
DEFAULT_FORMAT_CAPTION = "{status} {caption} {name}"
BUTTON_ID = 230


def _get_account_num():
    try:
        UserConfig = jclass("org.telegram.messenger.UserConfig")
        return int(UserConfig.selectedAccount)
    except Exception:
        return 0


def _is_home_dialogs(fragment):
    try:
        if fragment is None:
            return False
        class_name = fragment.getClass().getName()
        if class_name != "org.telegram.ui.DialogsActivity":
            return False
        try:
            folder_id = int(fragment.folderId)
            if folder_id != 0:
                return False
        except Exception:
            pass
        try:
            only_select = bool(fragment.onlySelect)
            if only_select:
                return False
        except Exception:
            pass
        return True
    except Exception:
        return False


def _has_sliding_fragment(fragment):
    try:
        container = fragment.rightSlidingDialogContainer
        if container is not None:
            try:
                if container.hasFragment():
                    return True
            except Exception:
                cf = get_private_field(container, "currentFragment")
                if cf is not None:
                    return True
    except Exception:
        pass
    return False


def _find_home_fragment():
    try:
        f = get_last_fragment()
        if f is not None and _is_home_dialogs(f):
            return f
    except Exception:
        pass
    try:
        f = get_last_fragment()
        if f is not None:
            layout = f.getParentLayout()
            if layout is not None:
                stack = layout.getFragmentStack()
                if stack is not None:
                    for i in range(stack.size()):
                        sf = stack.get(i)
                        if _is_home_dialogs(sf):
                            return sf
    except Exception:
        pass
    try:
        LaunchActivity = jclass("org.telegram.ui.LaunchActivity")
        f = LaunchActivity.getLastFragment()
        if f is not None and _is_home_dialogs(f):
            return f
    except Exception:
        pass
    try:
        LaunchActivity = jclass("org.telegram.ui.LaunchActivity")
        activity = LaunchActivity.instance
        if activity is not None:
            stack = activity.mainFragmentsStack
            if stack is not None:
                for i in range(stack.size()):
                    f = stack.get(i)
                    if _is_home_dialogs(f):
                        return f
    except Exception:
        pass
    try:
        LaunchActivity = jclass("org.telegram.ui.LaunchActivity")
        activity = LaunchActivity.instance
        if activity is not None:
            layout = activity.getActionBarLayout()
            if layout is not None:
                stack = layout.getFragmentStack()
                if stack is not None:
                    for i in range(stack.size()):
                        f = stack.get(i)
                        if _is_home_dialogs(f):
                            return f
    except Exception:
        pass
    return None


class DialogsCreateViewHook:
    def __init__(self, plugin):
        self.plugin = plugin

    def after_hooked_method(self, param):
        try:
            fragment = param.thisObject
            if not _is_home_dialogs(fragment):
                return
            self.plugin._sliding_open = False
            self.plugin._injected_btn = None
            run_on_ui_thread(lambda: self.plugin._inject_button(fragment), 300)
        except Exception:
            pass


class DialogsResumeHook:
    def __init__(self, plugin):
        self.plugin = plugin

    def after_hooked_method(self, param):
        try:
            fragment = param.thisObject
            if not _is_home_dialogs(fragment):
                return
            if _has_sliding_fragment(fragment):
                return
            run_on_ui_thread(lambda: self.plugin._inject_button(fragment), 100)
        except Exception:
            pass


class DialogsFullyVisibleHook:
    def __init__(self, plugin):
        self.plugin = plugin

    def after_hooked_method(self, param):
        try:
            fragment = param.thisObject
            if not _is_home_dialogs(fragment):
                return
            if _has_sliding_fragment(fragment):
                return
            run_on_ui_thread(lambda: self.plugin._inject_button(fragment), 200)
        except Exception:
            pass


class SlidingPresentHook:
    def __init__(self, plugin):
        self.plugin = plugin

    def after_hooked_method(self, param):
        try:
            self.plugin._on_sliding_opened()
        except Exception:
            pass


class SlidingFinishPreviewHook:
    def __init__(self, plugin):
        self.plugin = plugin

    def after_hooked_method(self, param):
        try:
            self.plugin._on_sliding_closed()
        except Exception:
            pass



# ============================================================
# MaxExteraPlugins Shared Author & Channel Subscription Module
# ============================================================

# ============================================================
# MaxExteraPlugins Shared Author & Channel Subscription Module
# ============================================================

# ============================================================
# MaxExteraPlugins Shared Author & Channel Subscription Module
# ============================================================
class AuthorChannelHelper:
    CONFIG_URL = "https://raw.githubusercontent.com/MaxExteraPlugins/config/main/links.json"

    DEFAULT_LINKS = {
        "channel_username": "MaxExteraPlugins",
        "channel_url": "https://t.me/MaxExteraPlugins",
        "trial_days": 7,
        "header": {"ru": "MaxExteraPlugins", "en": "MaxExteraPlugins"},
        "buttons": [
            {"title": {"ru": "Канал автора", "en": "Author's Channel"}, "icon": "msg_channel", "url": "https://t.me/MaxExteraPlugins"},
            {"title": {"ru": "Поддержать автора", "en": "Support author"}, "icon": "msg_share", "url": "https://t.me/itNotMax"},
            {"title": {"ru": "Сообщить о баге", "en": "Report a bug"}, "icon": "msg_help", "url": "https://t.me/itNotMax"}
        ]
    }

    _TEXTS = {
        "install_card_title": {"ru": "Спасибо за установку!", "en": "Thank you for installing!"},
        "install_card_msg": {
            "ru": "Надеемся, что плагин будет вам полезен!\n\nМы делаем плагины бесплатными и доступными для всех: пожалуйста, поддержите нас подпиской. Там будут только важные новости, обновления и розыгрыши.",
            "en": "We hope this plugin will be useful to you!\n\nWe keep our plugins free and open for everyone: please support us with a subscription. We only post key news, updates, and giveaways."
        },
        "subscribe_btn": {"ru": "Подписаться", "en": "Subscribe"},
        "remind_later_btn": {"ru": "Напомнить позже", "en": "Remind later"},
        "check_sub_btn": {"ru": "Проверить подписку", "en": "Check subscription"},
        "trial_expired_title": {"ru": "Пожалуйста, подпишитесь на канал", "en": "Please subscribe to the channel"},
        "trial_expired_msg": {
            "ru": "Пожалуйста, подпишитесь на наш официальный канал.\n\nМы делаем плагины бесплатно, ничего не требуя взамен. До подписки функции плагина временно приостановлены.",
            "en": "Please subscribe to our official channel.\n\nWe develop plugins for free and ask nothing in return. Plugin features are paused until you subscribe."
        },
        "sub_thank_you": {"ru": "Спасибо за подписку на наш канал!", "en": "Thank you for subscribing to our channel!"},
        "sub_thank_you_after_expired": {"ru": "Спасибо за подписку на наш канал!\nПлагин продолжит работу!", "en": "Thank you for subscribing to our channel!\nThe plugin will continue working!"},
        "sub_not_found": {"ru": "Подписка не обнаружена. Пожалуйста, подпишитесь на канал.", "en": "Subscription not found. Please subscribe to the channel."},
        "settings_channel": {"ru": "Канал автора", "en": "Author's Channel"},
        "settings_donate": {"ru": "Поддержать автора", "en": "Support author"},
        "settings_bug_report": {"ru": "Сообщить о баге", "en": "Report a bug"}
    }

    @classmethod
    def is_ru(cls) -> bool:
        try:
            from org.telegram.messenger import LocaleController
            cur = str(LocaleController.getInstance().getCurrentLocale().getLanguage() or "").lower()
            if cur.startswith(("ru", "uk", "be")): return True
            if cur: return False
        except Exception:
            pass
        try:
            from java.util import Locale
            code = str(Locale.getDefault().getLanguage() or "").lower()
            if code.startswith(("ru", "uk", "be")): return True
        except Exception:
            pass
        return False

    @classmethod
    def tr(cls, key: str) -> str:
        entry = cls._TEXTS.get(key, {})
        return entry.get("ru" if cls.is_ru() else "en", entry.get("en", key))

    def __init__(self, plugin, icon_sticker=None):
        self.plugin = plugin
        self.icon_sticker = icon_sticker or getattr(plugin, "__icon__", "MaxExteraPluginsStickers/1")
        self._stopped = False
        self._active_dialog = None
        self._last_known_sub = None

    def on_load(self):
        self._stopped = False
        self._active_dialog = None
        self._last_known_sub = None
        self._load_remote_links_async()
        self._check_initial_subscription_flow()
        self._start_subscription_watcher()

    def on_event(self, event_type):
        try:
            name = str(event_type).upper()
            if name.endswith("START") or name.endswith("RESUME"):
                self._check_subscription_change_instant()
        except Exception:
            pass

    def on_unload(self):
        self._stopped = True
        self._dismiss_active_dialog()

    def _get_links(self) -> dict:
        raw = self.plugin.get_setting("remote_links_cache", None)
        if raw:
            try:
                import json
                data = json.loads(raw)
                if isinstance(data, dict): return data
            except Exception:
                pass
        return self.DEFAULT_LINKS

    def _load_remote_links_async(self):
        def worker():
            try:
                import urllib.request, json
                req = urllib.request.Request(self.CONFIG_URL, headers={"User-Agent": "MaxExteraPlugins"})
                with urllib.request.urlopen(req, timeout=4) as resp:
                    if resp.status == 200:
                        data = json.loads(resp.read().decode("utf-8"))
                        if isinstance(data, dict):
                            self.plugin.set_setting("remote_links_cache", json.dumps(data))
                            self._resolve_channel_in_telegram(data.get("channel_username", "MaxExteraPlugins"))
            except Exception:
                pass
        import threading
        t = threading.Thread(target=worker, daemon=True)
        t.start()

    def _open_url(self, url: str, view=None):
        try:
            from org.telegram.messenger.browser import Browser
            from org.telegram.messenger import ApplicationLoader
            from client_utils import get_last_fragment
            ctx = None
            if view is not None:
                ctx = view.getContext()
            if ctx is None:
                frag = get_last_fragment()
                if frag is not None:
                    ctx = frag.getParentActivity()
            if ctx is None:
                ctx = ApplicationLoader.applicationContext
            Browser.openUrl(ctx, url)
        except Exception:
            pass

    def _resolve_channel_in_telegram(self, username: str):
        try:
            from org.telegram.messenger import UserConfig, MessagesController
            from org.telegram.tgnet import TLRPC, ConnectionsManager, RequestDelegate
            clean_user = username.lstrip("@")
            acc = int(UserConfig.selectedAccount)
            mc = MessagesController.getInstance(acc)
            if not mc: return
            req = TLRPC.TL_contacts_resolveUsername()
            req.username = clean_user
            helper_ref = self
            class Delegate(RequestDelegate):
                def run(self, response, error):
                    if error is None and response is not None:
                        chats = getattr(response, "chats", None)
                        if chats is not None and chats.size() > 0:
                            mc.putChats(chats, False)
                            c = chats.get(0)
                            cid = getattr(c, "id", 0)
                            if cid > 0:
                                helper_ref.plugin.set_setting("resolved_channel_id", int(cid))
            ConnectionsManager.getInstance(acc).sendRequest(req, Delegate())
        except Exception:
            pass

    def is_subscribed(self) -> bool:
        try:
            from org.telegram.messenger import UserConfig, MessagesController
            links = self._get_links()
            target = str(links.get("channel_username", "MaxExteraPlugins") or "MaxExteraPlugins").lower().lstrip("@")
            saved_cid = self.plugin.get_setting("resolved_channel_id", 0)

            for acc in range(UserConfig.MAX_ACCOUNT_COUNT):
                uconf = UserConfig.getInstance(acc)
                if not uconf.isClientActivated(): continue
                mc = MessagesController.getInstance(acc)
                if not mc: continue

                if saved_cid:
                    try:
                        from java.lang import Long as JLong
                        c = mc.getChat(JLong(int(saved_cid)))
                        if c is not None:
                            left = bool(getattr(c, "left", True))
                            kicked = bool(getattr(c, "kicked", False))
                            if not left and not kicked: return True
                    except Exception:
                        pass

                try:
                    chat = mc.getUserOrChat(target)
                    if chat is not None:
                        cid = getattr(chat, "id", 0)
                        if cid and not saved_cid:
                            self.plugin.set_setting("resolved_channel_id", int(cid))
                        left = bool(getattr(chat, "left", True))
                        kicked = bool(getattr(chat, "kicked", False))
                        if not left and not kicked: return True
                except Exception:
                    pass

                try:
                    dialogs = mc.allDialogs
                    if dialogs is not None:
                        limit = min(dialogs.size(), 300)
                        for i in range(limit):
                            d = dialogs.get(i)
                            did = getattr(d, "id", 0)
                            if did < 0:
                                from java.lang import Long as JLong
                                c = mc.getChat(JLong(-did))
                                if c is not None:
                                    uname = str(getattr(c, "username", "") or "").lower()
                                    if uname == target:
                                        cid = getattr(c, "id", 0)
                                        if cid and not saved_cid:
                                            self.plugin.set_setting("resolved_channel_id", int(cid))
                                        left = bool(getattr(c, "left", True))
                                        kicked = bool(getattr(c, "kicked", False))
                                        if not left and not kicked: return True
                except Exception:
                    pass
        except Exception:
            pass
        return False

    def is_allowed(self) -> bool:
        import time
        if self.is_subscribed():
            if not self.plugin.get_setting("was_subscribed", False):
                was_exp = bool(self.plugin.get_setting("was_expired_state", False))
                self.plugin.set_setting("was_subscribed", True)
                self.plugin.set_setting("was_expired_state", False)
                self._notify_subscribed(was_expired=was_exp)
            return True

        if self.plugin.get_setting("was_expired_state", False) or self.plugin.get_setting("was_subscribed", False):
            self.plugin.set_setting("was_subscribed", False)
            self.plugin.set_setting("was_expired_state", True)
            self._show_expired_card()
            return False

        now = time.time()
        install_time = float(self.plugin.get_setting("install_time", 0.0) or 0.0)
        if install_time <= 0:
            install_time = now
            self.plugin.set_setting("install_time", install_time)

        trial_days = float(self._get_links().get("trial_days", 7))
        trial_sec = trial_days * 86400.0

        if (now - install_time) < trial_sec:
            return True

        self.plugin.set_setting("was_expired_state", True)
        self._show_expired_card()
        return False

    def prepend_settings(self, original_items=None) -> list:
        from ui.settings import Header, Text, Divider

        # Prevent double-prepending
        if original_items and any(getattr(x, "text", "") == "MaxExteraPlugins" for x in original_items if type(x).__name__ == "Header"):
            return original_items

        links = self._get_links()
        buttons_config = links.get("buttons")

        author_items = []
        if isinstance(buttons_config, list):
            for btn in buttons_config:
                if not isinstance(btn, dict): continue
                raw_url = btn.get("url")
                if isinstance(raw_url, dict):
                    keys = [
                        getattr(self.plugin, "id", None),
                        globals().get("__id__", None),
                        globals().get("__name__", None),
                        self.plugin.__class__.__name__
                    ]
                    keys += [k.lower() for k in keys if isinstance(k, str)]
                    resolved_url = ""
                    for k in keys:
                        if k and k in raw_url:
                            resolved_url = str(raw_url[k] or "").strip()
                            if resolved_url:
                                break
                    url = resolved_url
                elif isinstance(raw_url, str):
                    url = raw_url.strip()
                else:
                    url = ""

                if not url: continue

                title_data = btn.get("title")
                if isinstance(title_data, dict):
                    title = title_data.get("ru" if self.is_ru() else "en") or title_data.get("en") or title_data.get("ru") or ""
                elif isinstance(title_data, str) and title_data:
                    title = title_data
                else:
                    title = btn.get("title_ru" if self.is_ru() else "title_en") or btn.get("title_ru") or btn.get("title_en") or ""

                if not title: continue
                icon = str(btn.get("icon") or "msg_channel").strip()

                def make_click(u):
                    return lambda v=None: self._open_url(u, v)

                author_items.append(Text(text=title, icon=icon, on_click=make_click(url)))
        else:
            for k, text_key, icon_name in [
                ("channel_url", "settings_channel", "msg_channel"),
                ("donate_url", "settings_donate", "msg_share"),
                ("bug_report_url", "settings_bug_report", "msg_help")
            ]:
                u = str(links.get(k) or "").strip()
                if u:
                    author_items.append(Text(text=self.tr(text_key), icon=icon_name, on_click=lambda v=None, target_u=u: self._open_url(target_u, v)))

        res = []
        if author_items:
            hdr = links.get("header") or "MaxExteraPlugins"
            if isinstance(hdr, dict):
                hdr_text = hdr.get("ru" if self.is_ru() else "en") or hdr.get("ru") or hdr.get("en") or "MaxExteraPlugins"
            else:
                hdr_text = str(hdr)
            res.append(Header(text=hdr_text))
            res.extend(author_items)
            res.append(Divider())

        # Clean original_items by removing any old "Информация" / "Information" category
        cleaned_items = []
        if original_items:
            skipping_info = False
            for item in original_items:
                item_cls = type(item).__name__
                if item_cls == "Header":
                    txt = str(getattr(item, "text", "") or getattr(item, "title", "") or "").lower()
                    if "информ" in txt or "inform" in txt:
                        skipping_info = True
                        continue
                    else:
                        skipping_info = False
                elif skipping_info and item_cls == "Divider":
                    skipping_info = False
                    continue

                if not skipping_info:
                    cleaned_items.append(item)

        res.extend(cleaned_items)
        return res

    def _dismiss_active_dialog(self):
        try:
            if self._active_dialog is not None:
                self._active_dialog.dismiss()
        except Exception:
            pass
        self._active_dialog = None

    def _is_dialog_active(self) -> bool:
        try:
            if self._active_dialog is not None:
                return bool(self._active_dialog.isShowing())
        except Exception:
            pass
        return False

    def _notify_subscribed(self, was_expired=False):
        self.plugin.set_setting("was_subscribed", True)
        from ui.bulletin import BulletinHelper
        msg_key = "sub_thank_you_after_expired" if was_expired else "sub_thank_you"
        BulletinHelper.show_success(self.tr(msg_key))

    def _check_subscription_change_instant(self):
        try:
            from android_utils import run_on_ui_thread
            cur_sub = self.is_subscribed()
            prev_sub = self._last_known_sub
            if prev_sub is not None and prev_sub != cur_sub:
                self._last_known_sub = cur_sub
                if cur_sub:
                    was_exp = bool(self.plugin.get_setting("was_expired_state", False))
                    self.plugin.set_setting("was_subscribed", True)
                    self.plugin.set_setting("was_expired_state", False)
                    self._dismiss_active_dialog()
                    self._notify_subscribed(was_expired=was_exp)
                else:
                    self.plugin.set_setting("was_subscribed", False)
                    self.plugin.set_setting("was_expired_state", True)
                    self._dismiss_active_dialog()
                    self._show_expired_card()
            else:
                self._last_known_sub = cur_sub
        except Exception:
            pass

    def _start_subscription_watcher(self):
        def watcher_loop():
            import time
            from android_utils import run_on_ui_thread
            time.sleep(2.0)
            if self._stopped: return
            self._last_known_sub = self.is_subscribed()

            while not self._stopped:
                try:
                    time.sleep(2.0)
                    if self._stopped: break
                    cur_sub = self.is_subscribed()
                    prev_sub = self._last_known_sub

                    if prev_sub is not None and prev_sub != cur_sub:
                        self._last_known_sub = cur_sub
                        if cur_sub:
                            was_exp = bool(self.plugin.get_setting("was_expired_state", False))
                            self.plugin.set_setting("was_subscribed", True)
                            self.plugin.set_setting("was_expired_state", False)
                            def on_sub():
                                self._dismiss_active_dialog()
                                self._notify_subscribed(was_expired=was_exp)
                            run_on_ui_thread(on_sub)
                        else:
                            self.plugin.set_setting("was_subscribed", False)
                            self.plugin.set_setting("was_expired_state", True)
                            def on_unsub():
                                self._dismiss_active_dialog()
                                self._show_expired_card()
                            run_on_ui_thread(on_unsub)
                    else:
                        self._last_known_sub = cur_sub
                except Exception:
                    pass
        import threading
        t = threading.Thread(target=watcher_loop, daemon=True)
        t.start()

    def _check_initial_subscription_flow(self):
        def flow():
            import time
            try:
                now = time.time()
                install_time = float(self.plugin.get_setting("install_time", 0.0) or 0.0)
                if install_time <= 0:
                    install_time = now
                    self.plugin.set_setting("install_time", install_time)

                is_sub = self.is_subscribed()
                self._last_known_sub = is_sub
                was_sub = bool(self.plugin.get_setting("was_subscribed", False))
                was_exp = bool(self.plugin.get_setting("was_expired_state", False))

                if is_sub:
                    if not was_sub:
                        self.plugin.set_setting("was_subscribed", True)
                        self.plugin.set_setting("was_expired_state", False)
                        self._notify_subscribed(was_expired=was_exp)
                    return

                if was_sub or was_exp:
                    self.plugin.set_setting("was_subscribed", False)
                    self.plugin.set_setting("was_expired_state", True)
                    self._show_expired_card()
                    return

                trial_days = float(self._get_links().get("trial_days", 7))
                trial_sec = trial_days * 86400.0
                last_remind = float(self.plugin.get_setting("last_remind_time", 0.0) or 0.0)

                if (now - install_time) < trial_sec:
                    if last_remind <= 0 or (now - last_remind) >= trial_sec:
                        self._show_welcome_card()
                else:
                    self.plugin.set_setting("was_expired_state", True)
                    self._show_expired_card()
            except Exception:
                pass
        from android_utils import run_on_ui_thread
        run_on_ui_thread(flow, 1500)

    def _create_card_content(self, act, title_text, message_text):
        try:
            from android.widget import LinearLayout, TextView
            from android.view import Gravity
            from android.graphics import Typeface
            from org.telegram.messenger import AndroidUtilities, UserConfig, MediaDataController
            from org.telegram.ui.ActionBar import Theme
            from org.telegram.ui.Components import BackupImageView

            dp = AndroidUtilities.dp
            layout = LinearLayout(act)
            layout.setOrientation(LinearLayout.VERTICAL)
            layout.setGravity(Gravity.CENTER_HORIZONTAL)
            layout.setPadding(dp(24), dp(16), dp(24), dp(6))

            size = dp(76)
            iv = BackupImageView(act)
            iv.setRoundRadius(dp(18))
            lp_iv = LinearLayout.LayoutParams(size, size)
            lp_iv.gravity = Gravity.CENTER_HORIZONTAL
            lp_iv.setMargins(0, dp(4), 0, dp(16))
            iv.setLayoutParams(lp_iv)

            try:
                acc = int(UserConfig.selectedAccount)
                mdc = MediaDataController.getInstance(acc)
                raw_icon = str(self.icon_sticker)
                if "/" in raw_icon:
                    pack, idx_s = raw_icon.split("/", 1)
                    mdc.setPlaceholderImageByIndex(iv, pack, int(idx_s), "150_150")
            except Exception:
                pass
            layout.addView(iv)

            if title_text:
                tt = TextView(act)
                tt.setText(title_text)
                tt.setTextSize(19.0)
                tt.setTypeface(None, Typeface.BOLD)
                tt.setTextColor(Theme.getColor(Theme.key_dialogTextBlack))
                tt.setGravity(Gravity.CENTER_HORIZONTAL)
                lp_t = LinearLayout.LayoutParams(-1, -2)
                lp_t.setMargins(0, 0, 0, dp(12))
                tt.setLayoutParams(lp_t)
                layout.addView(tt)

            if message_text:
                mt = TextView(act)
                mt.setText(message_text)
                mt.setTextSize(15.0)
                mt.setTextColor(Theme.getColor(Theme.key_dialogTextBlack))
                mt.setLineSpacing(float(dp(3)), 1.0)
                mt.setGravity(Gravity.CENTER_HORIZONTAL)
                lp_m = LinearLayout.LayoutParams(-1, -2)
                mt.setLayoutParams(lp_m)
                layout.addView(mt)

            return layout
        except Exception:
            return None

    def _show_welcome_card(self):
        def show():
            try:
                if self._is_dialog_active(): return
                from client_utils import get_last_fragment
                frag = get_last_fragment()
                if not frag: return
                act = frag.getParentActivity()
                if not act: return

                links = self._get_links()
                url = links.get("channel_url", "https://t.me/MaxExteraPlugins")

                from ui.alert import AlertDialogBuilder
                b = AlertDialogBuilder(act)
                content = self._create_card_content(act, self.tr("install_card_title"), self.tr("install_card_msg"))
                if content is not None:
                    b.set_view(content)
                else:
                    b.set_title(self.tr("install_card_title"))
                    b.set_message(self.tr("install_card_msg"))

                def on_sub(d, w):
                    self._dismiss_active_dialog()
                    self._open_url(url)
                    def check_after():
                        if self.is_subscribed():
                            self._notify_subscribed(was_expired=False)
                    from android_utils import run_on_ui_thread
                    run_on_ui_thread(check_after, 3000)

                def on_later(d, w):
                    import time
                    self._dismiss_active_dialog()
                    self.plugin.set_setting("last_remind_time", time.time())

                b.set_positive_button(self.tr("subscribe_btn"), on_sub)
                b.set_negative_button(self.tr("remind_later_btn"), on_later)
                self._active_dialog = b.show()
            except Exception:
                pass
        from android_utils import run_on_ui_thread
        run_on_ui_thread(show)

    def _show_expired_card(self):
        def show():
            try:
                if self._is_dialog_active(): return
                from client_utils import get_last_fragment
                frag = get_last_fragment()
                if not frag: return
                act = frag.getParentActivity()
                if not act: return

                links = self._get_links()
                url = links.get("channel_url", "https://t.me/MaxExteraPlugins")

                from ui.alert import AlertDialogBuilder
                from ui.bulletin import BulletinHelper
                b = AlertDialogBuilder(act)
                content = self._create_card_content(act, self.tr("trial_expired_title"), self.tr("trial_expired_msg"))
                if content is not None:
                    b.set_view(content)
                else:
                    b.set_title(self.tr("trial_expired_title"))
                    b.set_message(self.tr("trial_expired_msg"))

                def on_sub(d, w):
                    self._dismiss_active_dialog()
                    self._open_url(url)
                    def check_after():
                        if self.is_subscribed():
                            self.plugin.set_setting("was_subscribed", True)
                            self.plugin.set_setting("was_expired_state", False)
                            self._notify_subscribed(was_expired=True)
                    from android_utils import run_on_ui_thread
                    run_on_ui_thread(check_after, 3000)

                def on_check(d, w):
                    self._dismiss_active_dialog()
                    if self.is_subscribed():
                        self.plugin.set_setting("was_subscribed", True)
                        self.plugin.set_setting("was_expired_state", False)
                        self._notify_subscribed(was_expired=True)
                    else:
                        BulletinHelper.show_error(self.tr("sub_not_found"))
                        from android_utils import run_on_ui_thread
                        run_on_ui_thread(self._show_expired_card, 500)

                b.set_positive_button(self.tr("subscribe_btn"), on_sub)
                b.set_negative_button(self.tr("check_sub_btn"), on_check)
                self._active_dialog = b.show()
            except Exception:
                pass
        from android_utils import run_on_ui_thread
        run_on_ui_thread(show)


class EmojiNamePlugin(BasePlugin):
    def on_plugin_load(self):
        self._author_helper = AuthorChannelHelper(self, icon_sticker="MaxExteraPluginsStickers/16")
        self._author_helper.on_load()
        self._init_base_name()
        self._injected_btn = None
        self._home_fragment_ref = None
        self._alive = True
        self._sliding_open = False
        self._inject_gen = 0
        try:
            dialogs_clazz = find_class("org.telegram.ui.DialogsActivity")
            if dialogs_clazz:
                try:
                    self.hook_all_methods(dialogs_clazz, "createView", DialogsCreateViewHook(self))
                except Exception:
                    pass
                try:
                    self.hook_all_methods(dialogs_clazz, "onResume", DialogsResumeHook(self))
                except Exception:
                    pass
                try:
                    self.hook_all_methods(dialogs_clazz, "onBecomeFullyVisible", DialogsFullyVisibleHook(self))
                except Exception:
                    pass
        except Exception as e:
            log(f"EmojiName hook error: {e}")

        try:
            rsc_clazz = find_class("org.telegram.ui.RightSlidingDialogContainer")
            if rsc_clazz:
                self.hook_all_methods(rsc_clazz, "presentFragment", SlidingPresentHook(self))
                self.hook_all_methods(rsc_clazz, "finishPreview", SlidingFinishPreviewHook(self))
        except Exception:
            pass

        if self.get_setting("show_in_drawer", True):
            self._add_drawer_item()

        self._start_inject_loop()

    def on_plugin_unload(self):
        if hasattr(self, "_author_helper"):
            self._author_helper.on_unload()
        self._alive = False
        self._inject_gen += 1
        self._injected_btn = None
        self._home_fragment_ref = None
        self._remove_drawer_item()

    def on_app_event(self, event_type: AppEvent):
        if event_type in (AppEvent.START, AppEvent.RESUME):
            self._init_base_name()
            self._start_inject_loop()

    def _start_inject_loop(self):
        self._inject_gen += 1
        gen = self._inject_gen
        delays = [500, 1500, 3000, 6000, 10000]
        for d in delays:
            run_on_ui_thread(lambda g=gen: self._try_inject_gen(g), d)

    def _try_inject_gen(self, gen):
        if gen != self._inject_gen or not self._alive:
            return
        self._try_inject()

    def _get_key(self, name):
        return f"{name}_{_get_account_num()}"

    def _init_base_name(self):
        key = self._get_key("base_name")
        existing = self.get_setting(key, "")
        if not existing:
            try:
                uc = get_user_config()
                user = uc.getCurrentUser()
                if user:
                    first = getattr(user, "first_name", "") or ""
                    last = getattr(user, "last_name", "") or ""
                    full = (first + " " + last).strip() if last else first
                    self.set_setting(key, full)
            except Exception:
                pass

    def _get_base_name(self):
        key = self._get_key("base_name")
        val = self.get_setting(key, "") or ""
        if not val:
            self._init_base_name()
            val = self.get_setting(key, "") or ""
        return val

    def _add_drawer_item(self):
        self.add_menu_item(
            MenuItemData(
                menu_type=MenuItemType.DRAWER_MENU,
                text="Выбрать статус",
                on_click=self._on_drawer_click,
                icon="msg_emoji_smiles",
                item_id="emoji_name_drawer",
            )
        )

    def _remove_drawer_item(self):
        self.remove_menu_item("emoji_name_drawer")

    def _on_drawer_click(self, context: Dict[str, Any]):
        fragment = context.get("fragment")
        if fragment is None:
            fragment = get_last_fragment()
        if fragment is not None:
            self._show_emoji_picker(fragment)

    def _on_drawer_toggle(self, enabled: bool):
        if enabled:
            self._add_drawer_item()
        else:
            self._remove_drawer_item()

    def _try_inject(self):
        if not self.get_setting("show_on_main", True):
            return True
        try:
            fragment = _find_home_fragment()
            if fragment is not None:
                return self._inject_button(fragment)
        except Exception:
            pass
        return False

    def _on_sliding_opened(self):
        self._sliding_open = True
        try:
            btn = self._injected_btn
            if btn is not None:
                from android.view import View
                btn.setVisibility(View.GONE)
        except Exception:
            pass
        self._start_sliding_watcher()

    def _on_sliding_closed(self):
        self._sliding_open = False
        self._start_sliding_watcher()

    def _start_sliding_watcher(self):
        def watch():
            if not self._alive:
                return
            frag = self._home_fragment_ref
            if frag is None:
                self._sliding_open = False
                return
            if _has_sliding_fragment(frag):
                self._sliding_open = True
                try:
                    btn = self._injected_btn
                    if btn is not None:
                        from android.view import View
                        btn.setVisibility(View.GONE)
                except Exception:
                    pass
                run_on_ui_thread(watch, 300)
            else:
                self._sliding_open = False
                try:
                    btn = self._injected_btn
                    if btn is not None and self.get_setting("show_on_main", True):
                        from android.view import View
                        btn.setVisibility(View.VISIBLE)
                except Exception:
                    pass

        run_on_ui_thread(watch, 350)

    def _inject_button(self, fragment):
        try:
            if not self.get_setting("show_on_main", True):
                return True
            if not _is_home_dialogs(fragment):
                return False
            actionBar = fragment.getActionBar()
            if not actionBar:
                return False
            menu = actionBar.createMenu()
            if menu is None:
                return False
            existing = menu.getItem(BUTTON_ID)
            if existing is not None:
                self._injected_btn = existing
                self._home_fragment_ref = fragment
                return True
            R_drawable = jclass("org.telegram.messenger.R$drawable")
            item = menu.addItem(BUTTON_ID, R_drawable.msg_emoji_smiles)
            menu.removeView(item)
            idx = max(0, menu.getChildCount() - 2)
            menu.addView(item, idx)
            item.setOnClickListener(
                OnClickListener(lambda v: self._show_emoji_picker(fragment))
            )
            self._injected_btn = item
            self._home_fragment_ref = fragment
            if self._sliding_open:
                from android.view import View
                item.setVisibility(View.GONE)
            return True
        except Exception:
            return False

    def _get_templates(self):
        raw = self.get_setting("templates", "")
        if raw:
            try:
                data = json.loads(raw)
                if isinstance(data, list):
                    return data
            except Exception:
                pass
        return list(DEFAULT_TEMPLATES)

    def _save_templates(self, templates):
        self.set_setting("templates", json.dumps(templates, ensure_ascii=False), reload_settings=True)

    def _get_format(self):
        return self.get_setting("name_format", DEFAULT_FORMAT) or DEFAULT_FORMAT

    def _get_format_caption(self):
        return self.get_setting("name_format_caption", DEFAULT_FORMAT_CAPTION) or DEFAULT_FORMAT_CAPTION

    def _get_current_first_name(self):
        try:
            uc = get_user_config()
            user = uc.getCurrentUser()
            if user:
                return getattr(user, "first_name", "") or ""
        except Exception:
            pass
        return ""

    def _apply_template(self, template, fragment=None):
        try:
            uc = get_user_config()
            current_user = uc.getCurrentUser()
            if not current_user:
                BulletinHelper.show_error("Не удалось получить пользователя")
                return

            base_name = self._get_base_name()

            if template is None:
                new_first = base_name
            else:
                emoji = template.get("emoji", "")
                caption = template.get("caption", "")
                if caption:
                    fmt = self._get_format_caption()
                else:
                    fmt = self._get_format()
                new_first = fmt.replace("{name}", base_name).replace("{status}", emoji).replace("{caption}", caption)
                new_first = " ".join(new_first.split()).strip()

            TL_updateProfile = jclass("org.telegram.tgnet.tl.TL_account$updateProfile")
            req = TL_updateProfile()
            req.flags = 3
            req.first_name = new_first
            req.last_name = ""

            current_user.first_name = new_first
            current_user.last_name = ""

            mc = get_messages_controller()
            user_id = JLong(current_user.id)
            cached_user = mc.getUser(user_id)
            if cached_user is not None:
                cached_user.first_name = new_first
                cached_user.last_name = ""

            uc.saveConfig(True)

            NC = jclass("org.telegram.messenger.NotificationCenter")
            MessagesController = jclass("org.telegram.messenger.MessagesController")
            nc = get_notification_center()
            nc.postNotificationName(NC.mainUserInfoChanged)
            nc.postNotificationName(NC.updateInterfaces, JInteger(MessagesController.UPDATE_MASK_NAME))

            cm = get_connections_manager()
            display_name = new_first

            def on_response(response, error):
                if error:
                    run_on_ui_thread(
                        lambda: BulletinHelper.show_error("Ошибка обновления имени")
                    )
                else:
                    run_on_ui_thread(
                        lambda: BulletinHelper.show_success(f"Имя обновлено: {display_name}")
                    )

            from client_utils import RequestCallback
            cm.sendRequest(req, RequestCallback(on_response))

        except Exception as e:
            BulletinHelper.show_error(f"Ошибка: {e}")

    def _show_emoji_picker(self, fragment):
        try:
            context = fragment.getParentActivity()
            if not context:
                return

            templates = self._get_templates()

            from android.widget import LinearLayout, TextView, HorizontalScrollView
            from android.view import Gravity
            from android.util import TypedValue
            from android.graphics import Color
            AndroidUtilities = jclass("org.telegram.messenger.AndroidUtilities")
            Theme = jclass("org.telegram.ui.ActionBar.Theme")

            from org.telegram.ui.ActionBar import BottomSheet

            builder = BottomSheet.Builder(context)

            root = LinearLayout(context)
            root.setOrientation(LinearLayout.VERTICAL)
            root.setPadding(
                AndroidUtilities.dp(16),
                AndroidUtilities.dp(16),
                AndroidUtilities.dp(16),
                AndroidUtilities.dp(16),
            )

            title = TextView(context)
            title.setText("Выберите статус:")
            title.setTextSize(TypedValue.COMPLEX_UNIT_DIP, 18)
            title.setGravity(Gravity.CENTER)
            title.setTextColor(Theme.getColor(Theme.key_dialogTextBlack))
            title.setPadding(0, 0, 0, AndroidUtilities.dp(12))
            root.addView(title)

            scroll = HorizontalScrollView(context)
            scroll.setHorizontalScrollBarEnabled(False)

            inner = LinearLayout(context)
            inner.setOrientation(LinearLayout.HORIZONTAL)
            inner.setGravity(Gravity.CENTER)
            inner.setPadding(
                AndroidUtilities.dp(4),
                AndroidUtilities.dp(4),
                AndroidUtilities.dp(4),
                AndroidUtilities.dp(4),
            )

            sheet_ref = [None]

            for tpl in templates:
                emoji = tpl.get("emoji", "?")
                caption = tpl.get("caption", "")

                cell_layout = LinearLayout(context)
                cell_layout.setOrientation(LinearLayout.VERTICAL)
                cell_layout.setGravity(Gravity.CENTER_HORIZONTAL)
                lp = LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.WRAP_CONTENT,
                    LinearLayout.LayoutParams.WRAP_CONTENT,
                )
                lp.setMargins(
                    AndroidUtilities.dp(4),
                    AndroidUtilities.dp(4),
                    AndroidUtilities.dp(4),
                    AndroidUtilities.dp(4),
                )
                cell_layout.setLayoutParams(lp)

                emoji_tv = TextView(context)
                emoji_tv.setText(str(emoji))
                emoji_tv.setTextSize(TypedValue.COMPLEX_UNIT_DIP, 28)
                emoji_tv.setGravity(Gravity.CENTER)
                cell_size = AndroidUtilities.dp(48)
                emoji_tv.setLayoutParams(LinearLayout.LayoutParams(cell_size, cell_size))
                cell_layout.addView(emoji_tv)

                if caption:
                    cap_tv = TextView(context)
                    cap_tv.setText(str(caption))
                    cap_tv.setTextSize(TypedValue.COMPLEX_UNIT_DIP, 10)
                    cap_tv.setGravity(Gravity.CENTER)
                    cap_tv.setTextColor(Theme.getColor(Theme.key_dialogTextGray2))
                    cap_tv.setMaxLines(1)
                    cap_tv.setSingleLine(True)
                    cap_lp = LinearLayout.LayoutParams(
                        LinearLayout.LayoutParams.WRAP_CONTENT,
                        LinearLayout.LayoutParams.WRAP_CONTENT,
                    )
                    cap_tv.setLayoutParams(cap_lp)
                    cell_layout.addView(cap_tv)

                t = tpl
                cell_layout.setOnClickListener(
                    OnClickListener(lambda v, template=t: self._on_template_selected(template, sheet_ref, fragment))
                )
                inner.addView(cell_layout)

            scroll.addView(inner)
            root.addView(scroll)

            remove_btn = TextView(context)
            remove_btn.setText("✖ Сбросить имя")
            remove_btn.setTextSize(TypedValue.COMPLEX_UNIT_DIP, 15)
            remove_btn.setGravity(Gravity.CENTER)
            remove_btn.setTextColor(Color.parseColor("#FF3B30"))
            remove_btn.setPadding(0, AndroidUtilities.dp(14), 0, AndroidUtilities.dp(4))
            remove_btn.setOnClickListener(
                OnClickListener(lambda v: self._on_template_selected(None, sheet_ref, fragment))
            )
            root.addView(remove_btn)

            builder.setCustomView(root)
            sheet = builder.create()
            sheet_ref[0] = sheet
            sheet.show()

        except Exception as e:
            BulletinHelper.show_error(f"Ошибка: {e}")

    def _on_template_selected(self, template, sheet_ref, fragment):
        try:
            if sheet_ref[0]:
                sheet_ref[0].dismiss()
        except Exception:
            pass
        self._apply_template(template, fragment)

    def _make_template_click_handler(self, template):
        def handler(view):
            self._apply_template(template)
        return handler

    def _make_template_action_handler(self, index):
        def handler(view):
            templates = self._get_templates()
            if index < 0 or index >= len(templates):
                return
            tpl = templates[index]
            emoji = tpl.get("emoji", "")
            caption = tpl.get("caption", "")
            title = f"{emoji} ({caption})" if caption else emoji

            options = []
            option_actions = []

            options.append("✏️ Изменить")
            option_actions.append("edit")
            if index > 0:
                options.append("↑ Переместить вверх")
                option_actions.append("up")
            if index < len(templates) - 1:
                options.append("↓ Переместить вниз")
                option_actions.append("down")
            options.append("🗑 Удалить")
            option_actions.append("delete")

            ctx = view.getContext()

            def on_item(bld, idx):
                bld.dismiss()
                action = option_actions[idx]
                if action == "edit":
                    self._show_edit_template_dialog(ctx, index)
                elif action == "delete":
                    tpls = self._get_templates()
                    if 0 <= index < len(tpls):
                        removed = tpls.pop(index)
                        self._save_templates(tpls)
                        BulletinHelper.show_success(f"«{removed.get('emoji', '')}» удалён")
                elif action == "up":
                    tpls = self._get_templates()
                    if 0 <= index < len(tpls) and index - 1 >= 0:
                        tpls[index], tpls[index - 1] = tpls[index - 1], tpls[index]
                        self._save_templates(tpls)
                elif action == "down":
                    tpls = self._get_templates()
                    if 0 <= index < len(tpls) and index + 1 < len(tpls):
                        tpls[index], tpls[index + 1] = tpls[index + 1], tpls[index]
                        self._save_templates(tpls)

            alert = AlertDialogBuilder(ctx)
            alert.set_title(title)
            alert.set_items(options, on_item)
            alert.show()

        return handler

    def _show_edit_template_dialog(self, ctx, index):
        try:
            templates = self._get_templates()
            if index < 0 or index >= len(templates):
                return
            tpl = templates[index]

            from android.widget import LinearLayout, EditText
            from android.util import TypedValue
            AndroidUtilities = jclass("org.telegram.messenger.AndroidUtilities")
            Theme = jclass("org.telegram.ui.ActionBar.Theme")

            root = LinearLayout(ctx)
            root.setOrientation(LinearLayout.VERTICAL)
            root.setPadding(
                AndroidUtilities.dp(24),
                AndroidUtilities.dp(8),
                AndroidUtilities.dp(24),
                AndroidUtilities.dp(0),
            )

            emoji_input = EditText(ctx)
            emoji_input.setHint("Эмодзи")
            emoji_input.setText(tpl.get("emoji", ""))
            emoji_input.setTextSize(TypedValue.COMPLEX_UNIT_DIP, 16)
            emoji_input.setTextColor(Theme.getColor(Theme.key_dialogTextBlack))
            emoji_input.setHintTextColor(Theme.getColor(Theme.key_dialogTextHint))
            emoji_input.setSingleLine(True)
            root.addView(emoji_input)

            caption_input = EditText(ctx)
            caption_input.setHint("Подпись (необязательно)")
            caption_input.setText(tpl.get("caption", ""))
            caption_input.setTextSize(TypedValue.COMPLEX_UNIT_DIP, 16)
            caption_input.setTextColor(Theme.getColor(Theme.key_dialogTextBlack))
            caption_input.setHintTextColor(Theme.getColor(Theme.key_dialogTextHint))
            caption_input.setSingleLine(True)
            lp = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT,
            )
            lp.topMargin = AndroidUtilities.dp(8)
            caption_input.setLayoutParams(lp)
            root.addView(caption_input)

            def on_save(bld, which):
                emoji_val = str(emoji_input.getText()).strip()
                caption_val = str(caption_input.getText()).strip()
                if not emoji_val:
                    BulletinHelper.show_error("Введите эмодзи")
                    return
                tpls = self._get_templates()
                if index < 0 or index >= len(tpls):
                    bld.dismiss()
                    return
                for j, t in enumerate(tpls):
                    if j != index and t.get("emoji") == emoji_val and t.get("caption", "") == caption_val:
                        BulletinHelper.show_error("Такой шаблон уже есть")
                        return
                tpls[index] = {"emoji": emoji_val, "caption": caption_val}
                self._save_templates(tpls)
                BulletinHelper.show_success(f"Изменён: {emoji_val}")
                bld.dismiss()

            alert = AlertDialogBuilder(ctx)
            alert.set_title("Изменить шаблон")
            alert.set_view(root)
            alert.set_positive_button("Сохранить", on_save)
            alert.set_negative_button("Отмена", lambda bld, which: bld.dismiss())
            alert.show()

        except Exception as e:
            BulletinHelper.show_error(f"Ошибка: {e}")

    def _on_add_template_click(self, view):
        try:
            ctx = view.getContext()

            from android.widget import LinearLayout, EditText
            from android.util import TypedValue
            AndroidUtilities = jclass("org.telegram.messenger.AndroidUtilities")
            Theme = jclass("org.telegram.ui.ActionBar.Theme")

            root = LinearLayout(ctx)
            root.setOrientation(LinearLayout.VERTICAL)
            root.setPadding(
                AndroidUtilities.dp(24),
                AndroidUtilities.dp(8),
                AndroidUtilities.dp(24),
                AndroidUtilities.dp(0),
            )

            emoji_input = EditText(ctx)
            emoji_input.setHint("Эмодзи")
            emoji_input.setTextSize(TypedValue.COMPLEX_UNIT_DIP, 16)
            emoji_input.setTextColor(Theme.getColor(Theme.key_dialogTextBlack))
            emoji_input.setHintTextColor(Theme.getColor(Theme.key_dialogTextHint))
            emoji_input.setSingleLine(True)
            root.addView(emoji_input)

            caption_input = EditText(ctx)
            caption_input.setHint("Подпись (необязательно)")
            caption_input.setTextSize(TypedValue.COMPLEX_UNIT_DIP, 16)
            caption_input.setTextColor(Theme.getColor(Theme.key_dialogTextBlack))
            caption_input.setHintTextColor(Theme.getColor(Theme.key_dialogTextHint))
            caption_input.setSingleLine(True)
            lp = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT,
            )
            lp.topMargin = AndroidUtilities.dp(8)
            caption_input.setLayoutParams(lp)
            root.addView(caption_input)

            def on_save(bld, which):
                emoji_val = str(emoji_input.getText()).strip()
                caption_val = str(caption_input.getText()).strip()
                if not emoji_val:
                    BulletinHelper.show_error("Введите эмодзи")
                    return
                templates = self._get_templates()
                for t in templates:
                    if t.get("emoji") == emoji_val and t.get("caption", "") == caption_val:
                        BulletinHelper.show_error("Такой шаблон уже есть")
                        return
                templates.append({"emoji": emoji_val, "caption": caption_val})
                self._save_templates(templates)
                BulletinHelper.show_success(f"Добавлен: {emoji_val}")
                bld.dismiss()

            alert = AlertDialogBuilder(ctx)
            alert.set_title("Новый шаблон")
            alert.set_view(root)
            alert.set_positive_button("Сохранить", on_save)
            alert.set_negative_button("Отмена", lambda bld, which: bld.dismiss())
            alert.show()

        except Exception as e:
            BulletinHelper.show_error(f"Ошибка: {e}")

    def _on_reset_templates_click(self, view):
        self._save_templates(list(DEFAULT_TEMPLATES))
        BulletinHelper.show_success("Шаблоны сброшены")

    def _on_remove_current_click(self, view):
        self._apply_template(None)

    def _open_url(self, url):
        def handler(view):
            try:
                Browser = jclass("org.telegram.messenger.browser.Browser")
                ctx = view.getContext()
                Browser.openUrl(ctx, url)
            except Exception:
                BulletinHelper.show_error("Не удалось открыть ссылку")
        return handler

    def _create_manage_page(self) -> List[Any]:
        items = []
        templates = self._get_templates()
        items.append(Header(text=f"Шаблоны ({len(templates)})"))

        for i, tpl in enumerate(templates):
            emoji = tpl.get("emoji", "")
            caption = tpl.get("caption", "")
            label = f"{emoji}"
            if caption:
                label = f"{emoji} ({caption})"
            items.append(
                Text(
                    text=label,
                    icon="msg_emoji_recent",
                    on_click=self._make_template_action_handler(i),
                )
            )

        items.append(Divider())
        items.append(
            Text(
                text="Добавить шаблон",
                icon="msg_add",
                on_click=self._on_add_template_click,
            )
        )
        items.append(Divider())
        items.append(
            Text(
                text="Сбросить шаблоны",
                icon="msg_retry",
                red=True,
                on_click=self._on_reset_templates_click,
            )
        )
        if hasattr(self, "_author_helper"):

            return self._author_helper.prepend_settings(items)

        return items

    def create_settings(self):
        try:
            items = self._inner_create_settings()
        except Exception:
            items = []
        if hasattr(self, '_author_helper'):
            return self._author_helper.prepend_settings(items)
        return items

    def _inner_create_settings(self):
        items = []

        items.append(Header(text="Информация"))
        items.append(
            Text(
                text="Документация",
                icon="msg_link",
                on_click=self._open_url("https://telegra.ph/Dokumentaciya-k-plaginu-Status-Adder-06-23"),
            )
        )
        items.append(
            Text(
                text="Канал автора",
                icon="msg_channel",
                on_click=self._open_url("https://t.me/MaxExteraPlugins"),
            )
        )
        items.append(Divider())

        items.append(Header(text="Стандартное имя"))
        items.append(
            Input(
                key=self._get_key("base_name"),
                text="Имя для сброса",
                default=self._get_base_name(),
                subtext="При сбросе шаблона имя вернётся к этому значению",
                icon="msg_edit",
            )
        )
        items.append(
            Text(
                text="Сбросить имя",
                subtext="Отменить использованный шаблон",
                icon="msg_delete",
                red=True,
                on_click=self._on_remove_current_click,
            )
        )
        items.append(Divider())

        items.append(Header(text="Шаблоны"))
        items.append(
            Input(
                key="name_format",
                text="Без подписи",
                default=DEFAULT_FORMAT,
            )
        )
        items.append(
            Input(
                key="name_format_caption",
                text="С подписью",
                default=DEFAULT_FORMAT_CAPTION,
            )
        )

        items.append(Divider())

        items.append(Header(text="Кнопка доступа"))
        items.append(
            Switch(
                key="show_on_main",
                text="На главном экране",
                default=True,
            )
        )
        items.append(
            Switch(
                key="show_in_drawer",
                text="В боковом меню",
                default=True,
                on_change=self._on_drawer_toggle,
            )
        )
        items.append(Divider())

        templates = self._get_templates()
        items.append(Header(text=f"Шаблоны ({len(templates)})"))
        items.append(
            Text(
                text="Редактировать шаблоны",
                icon="msg_edit",
                create_sub_fragment=self._create_manage_page,
            )
        )

        for tpl in templates:
            emoji = tpl.get("emoji", "")
            caption = tpl.get("caption", "")
            sub = f"{caption}" if caption else ""
            items.append(
                Text(
                    text=f"{emoji}",
                    subtext=sub,
                    icon="msg_emoji_recent",
                    on_click=self._make_template_click_handler(tpl),
                )
            )

        return items
