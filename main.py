import dataclasses
import json
from typing import Dict, List

from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.action.ExtensionCustomAction import \
    ExtensionCustomAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import \
    RenderResultListAction
from urllib import request


def http_request(page: str):
    ret = request.urlopen(page)
    by = ret.read()
    return by.decode()


@dataclasses.dataclass
class Tab:
    id: str
    title: str
    url: str


def get_tabs() -> List[Tab]:
    res = http_request("http://127.0.0.1:9222/json")
    ls: List[Dict] = json.loads(res)
    filtered = map(
        lambda x: Tab(title=x["title"], url=x["url"], id=x["id"]),
        filter(
            lambda x: x["type"] == "page",
            ls
        )
    )
    return list(filtered)


def activate_tab(tab_id: str):
    http_request(f"http://127.0.0.1:9222/json/activate/{tab_id}")


class DemoExtension(Extension):
    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())


class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        # event is instance of ItemEnterEvent

        activate_tab(event.get_data())


class KeywordQueryEventListener(EventListener):
    def on_event(self, event: KeywordQueryEvent, extension):
        try:
            items = []
            tabs = get_tabs()

            tabs = filter(
                lambda x: ((event.get_argument() or "") in x.title) or (
                    (event.get_argument() or "") in x.url),
                tabs
            )

            tabs = list(tabs)[:5]

            for i in tabs:
                items.append(ExtensionResultItem(icon='images/icon.png',
                                                 name=i.title,
                                                 description=i.url,
                                                 on_enter=ExtensionCustomAction(
                                                     i.id,
                                                     keep_app_open=False)))

            return RenderResultListAction(items)
        except:
            return RenderResultListAction(
                [ExtensionResultItem(icon='images/icon.png',
                                     name="Can't reach chromium",
                                     description="",
                                     on_enter=HideWindowAction())])


if __name__ == '__main__':
    DemoExtension().run()
