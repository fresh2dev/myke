"""> Functions for reading."""

import sys
from functools import partial, wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Union

if sys.version_info >= (3, 10):
    from typing import TypeGuard
else:
    from typing_extensions import TypeGuard


class read(str):
    def __new__(cls, path: str, encoding: str = "utf-8") -> str:  # type: ignore
        return cls.text(path=path, encoding=encoding)

    @staticmethod
    def _is_simple_dict(candidate: Any) -> TypeGuard[Dict[str, Any]]:
        return isinstance(candidate, dict) and all(
            isinstance(k, str) for k in candidate
        )

    @classmethod
    def _read_simple_dict(
        cls,
        reader: Callable[..., Any],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        content: Any = reader(**kwargs)
        if not cls._is_simple_dict(content):
            raise TypeError("expected a dictionary with string keys")
        return content

    @staticmethod
    def text(path: Union[str, Path], encoding: str = "utf-8") -> str:
        """Read text file contents and strip surrounding whitespace.

        Equivalent to: `Path(path).read_text().strip()`

        Args:
            path: ...
            encoding: ...

        Returns:
            ...

        Examples:
            >>> import myke
            ...
            >>> myke.read.text('/path/to/file.txt')  # doctest: +SKIP
        """
        if isinstance(path, str):
            path = Path(path)
        return path.read_text(encoding=encoding).strip()

    @classmethod
    @wraps(text)
    def lines(cls, *args: str, **kwargs: str) -> List[str]:
        """Read lines from a text file, strip whitespace from each line, and return list of non-empty elements.

        Args:
            *args: ...
            **kwargs: ...

        Returns:
            ...

        Examples:
            >>> import myke
            ...
            >>> myke.read.lines('/path/to/file.txt')  # doctest: +SKIP
        """
        return [
            y for x in cls.text(*args, **kwargs).splitlines() for y in [x.strip()] if y
        ]

    @classmethod
    @wraps(text)
    def json(cls, *args: str, **kwargs: str) -> Dict[str, Any]:
        """Parse object(s) from a JSON text file.

        Args:
            *args: ...
            **kwargs: ...

        Returns:
            ...

        Examples:
            >>> import myke
            ...
            >>> myke.read.json('/path/to/file.json')  # doctest: +SKIP
        """
        import json as _json

        return cls._read_simple_dict(partial(_json.loads, cls.text(*args, **kwargs)))

    @classmethod
    @wraps(text)
    def yaml(cls, *args: str, **kwargs: str) -> Dict[str, Any]:
        """Parse object(s) from a YAML text file.

        Args:
            *args: ...
            **kwargs: ...

        Returns:
            ...

        Examples:
            >>> import myke
            ...
            >>> myke.read.yaml('/path/to/file.yaml')  # doctest: +SKIP
        """
        import yaml as _yaml

        return cls._read_simple_dict(
            partial(_yaml.safe_load, cls.text(*args, **kwargs)),
        )

    @classmethod
    @wraps(text)
    def yaml_all(cls, *args: str, **kwargs: str) -> List[Dict[str, Any]]:
        """Parse object(s) from multiple documents in a single YAML text file.

        Args:
            *args: ...
            **kwargs: ...

        Returns:
            ...

        Examples:
            >>> import myke
            ...
            >>> myke.read.yaml_all('/path/to/file.yaml')  # doctest: +SKIP
        """
        import yaml as _yaml

        def _yaml_all(txt: str) -> List[Dict[str, Any]]:
            return [
                cls._read_simple_dict(lambda y: y, y=x)
                for x in _yaml.safe_load_all(txt)
            ]

        return _yaml_all(cls.text(*args, **kwargs))

    @classmethod
    @wraps(text)
    def toml(cls, *args: str, **kwargs: str) -> Dict[str, Any]:
        """Parse object(s) from a TOML text file.

        Args:
            *args: ...
            **kwargs: ...

        Returns:
            ...

        Examples:
            >>> import myke
            ...
            >>> myke.read.toml('/path/to/file.toml')  # doctest: +SKIP
        """
        if sys.version_info >= (3, 11):
            import tomllib as _toml
        else:
            import tomli as _toml

        return cls._read_simple_dict(partial(_toml.loads, cls.text(*args, **kwargs)))

    @classmethod
    @wraps(text)
    def cfg(cls, *args: str, **kwargs: str) -> Dict[str, Any]:
        """Parse object(s) from a INI/CFG text file.

        Args:
            *args: ...
            **kwargs: ...

        Returns:
            ...

        Examples:
            >>> import myke
            ...
            >>> myke.read.cfg('/path/to/file.cfg')  # doctest: +SKIP
        """
        from configparser import ConfigParser

        def _read_cfg(txt: str) -> Dict[str, Any]:
            cp = ConfigParser()
            cp.read_string(txt)
            return {x: dict(cp.items(x)) for x in cp.sections()}

        return cls._read_simple_dict(partial(_read_cfg, cls.text(*args, **kwargs)))

    @classmethod
    @wraps(cfg)
    def ini(cls, *args: str, **kwargs: str) -> Dict[str, Any]:
        """Parse object(s) from a INI/CFG text file.

        Args:
            *args: ...
            **kwargs: ...

        Returns:
            ...

        Examples:
            >>> import myke
            ...
            >>> myke.read.ini('/path/to/file.ini')  # doctest: +SKIP
        """
        return cls.cfg(*args, **kwargs)

    @classmethod
    @wraps(text)
    def dotfile(cls, *args: str, **kwargs: str) -> Dict[str, str]:
        """Parse key-value pairs from a dotfile (aka "envfile").

        Args:
            *args: ...
            **kwargs: ...

        Returns:
            ...

        Examples:
            >>> import myke
            ...
            >>> myke.read.dotfile('/path/to/vars.env')  # doctest: +SKIP
        """
        from io import StringIO

        from dotenv import dotenv_values

        return cls._read_simple_dict(
            partial(dotenv_values, stream=StringIO(cls.text(*args, **kwargs))),
        )

    @classmethod
    @wraps(dotfile)
    def envfile(cls, *args: str, **kwargs: str) -> Dict[str, str]:
        """Parse key-value pairs from a dotfile (aka "envfile").

        Args:
            *args: ...
            **kwargs: ...

        Returns:
            ...

        Examples:
            >>> import myke
            ...
            >>> myke.read.envfile('/path/to/vars.env')  # doctest: +SKIP
        """
        return cls.dotfile(*args, **kwargs)

    @staticmethod
    def _url(addr: str, **kwargs: Any) -> Any:
        import requests

        addr = kwargs.pop("url", addr)
        method: str = kwargs.pop("method", "GET")
        timeout: float = kwargs.pop("timeout", 10)
        resp: requests.Response = requests.request(
            method=method,
            url=addr,
            timeout=timeout,
            **kwargs,
        )
        return resp

    @classmethod
    def url(cls, addr: str, **kwargs: Any) -> str:
        """Return text from HTTP GET response.

        Arguments:
            addr: URL of the remote file.
            **kwargs: passed to `requests.request`

        Returns:
            ...

        Examples:
            >>> import myke
            ...
            >>> myke.read.url('https://github.com/.../README.md')  # doctest: +SKIP
        """
        resp_text: str = cls._url(addr=addr, **kwargs).text
        return resp_text

    @classmethod
    def url_json(cls, addr: str, **kwargs: Any) -> Dict[str, Any]:
        """Parse JSON from HTTP GET response.

        Arguments:
            addr: URL of the remote file.
            **kwargs: passed to `requests.request`

        Returns:
            ...

        Examples:
            >>> import myke
            ...
            >>> myke.read.url_json('https://github.com/.../data.json')  # doctest: +SKIP
        """
        resp: Any = cls._url(addr=addr, **kwargs).json()
        resp_dict: Dict[str, Any] = cls._read_simple_dict(lambda: resp)
        return resp_dict
