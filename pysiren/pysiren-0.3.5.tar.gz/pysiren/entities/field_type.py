from enum import Enum


class FieldType(Enum):
    HIDDEN = "hidden"
    TEXT = "text"
    SEARCH = "search"
    TEL = "tel"
    URL = "url"
    EMAIL = "email"
    PASSWORD = "password"
    DATETIME = "datetime"
    DATE = "date"
    MONTH = "month"
    WEEK = "week"
    TIME = "time"
    DATETIME_LOCAL = "datetime-local"
    NUMBER = "number"
    RANGE = "range"
    COLOR = "color"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    FILE = "file"
