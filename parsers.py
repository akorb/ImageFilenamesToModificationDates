import functools
import re
from abc import abstractmethod
from datetime import datetime


class FileNameToDateParser:
    @staticmethod
    @functools.cache
    def get_all_parsers() -> list:
        parsers = [
            GenericFileNameToDateParser(),
            TimestampFileNameToDateParser(),
        ]
        return parsers

    def __init__(self, name: str, regex: re.Pattern[str]) -> None:
        self.name = name
        self.regex = regex

    def _to_tokens(self, filename: str) -> tuple[str]:
        res = self.regex.search(filename)
        if res is None:
            return None
        return res.groups() if res is not None else res

    @abstractmethod
    def _tokens_to_date(self, tokens: tuple[str]) -> datetime:
        raise NotImplementedError

    def parse(self, filename: str) -> datetime:
        tokens = self._to_tokens(filename)
        if tokens is None:
            return None
        date = self._tokens_to_date(tokens)
        return date

    @staticmethod
    def try_parse_with_all(filename: str) -> tuple[str, datetime]:
        parsers = FileNameToDateParser.get_all_parsers()
        for parser in parsers:
            date = parser.parse(filename)
            if date is not None:
                return parser.name, date
        return None, None


class GenericFileNameToDateParser(FileNameToDateParser):
    def __init__(self) -> None:
        # Such that regex doesn't start to match in the middle of a numerical string
        start = r'(?:^|[^0-9])'
        separator = r'[\-_]?'
        date = r'((?:19|20)[0-9]{2}[01][0-9][0-3][0-9])'
        time = r'([0-2][0-9](?:[0-6][0-9]){2})?'
        milliseconds = r'([0-9]{3})?'
        final_regex = start + date + separator + time + milliseconds
        super().__init__(
            "Generic",
            re.compile(final_regex)
        )

    def _tokens_to_date(self, tokens: tuple[str, str, str]) -> datetime:
        # <date>, <time>, <milliseconds>
        # e.g., ('20190916', '152241', '512')
        match tokens:
            case date, None, None:
                date = datetime.strptime(date, '%Y%m%d')
            case date, time, None:
                date = datetime.strptime(date + time, '%Y%m%d%H%M%S')
            case date, time, milliseconds:
                date = datetime.strptime(date + time + milliseconds, '%Y%m%d%H%M%S%f')
            case _:
                raise ValueError("Unexpected tokens.", tokens)
        return date


class TimestampFileNameToDateParser(FileNameToDateParser):
    def __init__(self) -> None:
        super().__init__(
            "Timestamp",
            re.compile(r'(1[0-9]{9,})')
        )

    def _tokens_to_date(self, tokens: tuple[str]) -> tuple[str, str]:
        # e.g., ('1568291659773',)
        timestamp_str, = tokens
        timestamp = int(timestamp_str)
        date = datetime.fromtimestamp(timestamp / 1000)
        return date
