import sys

# import urllib.request
from functools import partial, wraps
from typing import Any, Callable, Dict, List

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
    def text(path: str, encoding: str = "utf-8") -> str:
        with open(path, encoding=encoding) as f:
            return f.read().strip()

    @classmethod
    @wraps(text)
    def lines(cls, *args: str, **kwargs: str) -> List[str]:
        return [
            y for x in cls.text(*args, **kwargs).splitlines() for y in [x.strip()] if y
        ]

    @classmethod
    @wraps(text)
    def json(cls, *args: str, **kwargs: str) -> Dict[str, Any]:
        import json as _json

        return cls._read_simple_dict(partial(_json.loads, cls.text(*args, **kwargs)))

    @classmethod
    @wraps(text)
    def yaml(cls, *args: str, **kwargs: str) -> Dict[str, Any]:
        import yaml as _yaml

        return cls._read_simple_dict(
            partial(_yaml.safe_load, cls.text(*args, **kwargs)),
        )

    @classmethod
    @wraps(text)
    def yaml_all(cls, *args: str, **kwargs: str) -> List[Dict[str, Any]]:
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
        try:
            import tomli as _toml
        except ImportError:
            import tomllib as _toml

        return cls._read_simple_dict(partial(_toml.loads, cls.text(*args, **kwargs)))

    @classmethod
    @wraps(text)
    def cfg(cls, *args: str, **kwargs: str) -> Dict[str, Any]:
        from configparser import ConfigParser

        def _read_cfg(txt: str) -> Dict[str, Any]:
            cp = ConfigParser()
            cp.read_string(txt)
            return {x: dict(cp.items(x)) for x in cp.sections()}

        return cls._read_simple_dict(partial(_read_cfg, cls.text(*args, **kwargs)))

    @classmethod
    @wraps(cfg)
    def ini(cls, *args: str, **kwargs: str) -> Dict[str, Any]:
        return cls.cfg(*args, **kwargs)

    @classmethod
    @wraps(text)
    def dotfile(cls, *args: str, **kwargs: str) -> Dict[str, str]:
        from io import StringIO

        from dotenv import dotenv_values

        return cls._read_simple_dict(
            partial(dotenv_values, stream=StringIO(cls.text(*args, **kwargs))),
        )

    @classmethod
    @wraps(dotfile)
    def envfile(cls, *args: str, **kwargs: str) -> Dict[str, str]:
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
        resp_text: str = cls._url(addr=addr, **kwargs).text
        return resp_text

    @classmethod
    def url_dict(cls, addr: str, **kwargs: Any) -> Dict[str, Any]:
        resp: Any = cls._url(addr=addr, **kwargs).json()
        resp_dict: Dict[str, Any] = cls._read_simple_dict(lambda: resp)
        return resp_dict
