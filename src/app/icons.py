"""Иконки интерфейса — Material Symbols (https://fonts.google.com/icons).

Шрифт загружается подмножеством только с перечисленными иконками (~6 КБ вместо ~400 КБ),
поэтому иконка, которой нет в списке, отобразится текстом. Новая иконка — в том числе
для новой категории — сначала добавляется сюда.
"""

from flask import Flask

UI_ICONS = frozenset({
    "add", "calendar_add_on", "calendar_today", "check", "check_circle", "close",
    "confirmation_number", "contrast", "dark_mode", "edit", "error", "event", "event_available",
    "grid_view", "group", "info", "label", "light_mode", "location_on", "lock", "lock_person",
    "person", "person_add", "schedule", "search", "sell", "shield", "warning",
})

# Значения categories.icon в БД
CATEGORY_ICONS = frozenset({
    "celebration", "hiking", "menu_book", "music_note", "palette", "school", "science",
    "sports_esports", "sports_soccer",
})

DEFAULT_CATEGORY_ICON = "label"

_FONT_URL = (
    "https://fonts.googleapis.com/css2"
    "?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,1,0"
    "&icon_names={names}&display=block"
)


def category_icon(name: str | None) -> str:
    """Иконка категории, которую точно есть чем нарисовать."""
    return name if name in CATEGORY_ICONS else DEFAULT_CATEGORY_ICON


def icon_font_url() -> str:
    # Google Fonts требует имена в алфавитном порядке
    return _FONT_URL.format(names=",".join(sorted(UI_ICONS | CATEGORY_ICONS)))


def register_icons(app: Flask) -> None:
    font_url = icon_font_url()

    @app.context_processor
    def inject_icons():
        return {"icon_font_url": font_url, "category_icon": category_icon}
