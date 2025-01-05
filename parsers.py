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
        return res.groupdict()

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
        date = r'(?P<year>(?:19|20)[0-9]{2})' + separator + r'(?P<month>[01][0-9])' + separator + r'(?P<day>[0-3][0-9])'
        time = r'(?P<hour>[0-2][0-9])?' + separator + '(?P<minute>[0-6][0-9])?' + separator + '(?P<second>[0-6][0-9])?'
        milliseconds = r'(?P<millisecond>[0-9]{3})?'
        final_regex = start + date + separator + time + separator + milliseconds

        super().__init__(
            "Generic",
            re.compile(final_regex)
        )

    def _tokens_to_date(self, tokens: dict[str, str]) -> datetime:
        tokens = {k: int(v or 0) for k, v in tokens.items()}
        tokens['microsecond'] = tokens.pop('millisecond') * 1000
        date = datetime(**tokens)
        return date


class TimestampFileNameToDateParser(FileNameToDateParser):
    def __init__(self) -> None:
        super().__init__(
            "Timestamp",
            re.compile(r'(?P<timestamp>1[0-9]{9,})')
        )

    def _tokens_to_date(self, tokens: dict[str, str]) -> tuple[str, str]:
        timestamp_str = tokens['timestamp']
        timestamp = int(timestamp_str)
        date = datetime.fromtimestamp(timestamp / 1000)
        return date
