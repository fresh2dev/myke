__all__ = ["text", "lines", "json", "yaml", "cfg", "dotfile", "envfile"]

# import urllib.request
from functools import partial, wraps
from typing import Any, Callable, Dict, List

try:
    from typing_extensions import TypeGuard
except ImportError:
    from typing import TypeGuard


def _is_simple_dict(candidate: Any) -> TypeGuard[Dict[str, Any]]:
    return isinstance(candidate, dict) and all(isinstance(k, str) for k in candidate)


def _read_simple_dict(reader: Callable[..., Any], **kwargs: Any) -> Dict[str, Any]:
    content: Any = reader(**kwargs)
    if not _is_simple_dict(content):
        raise TypeError("expected a dictionary with string keys")
    return content


def text(path: str, encoding: str = "utf-8") -> str:
    with open(path, "r", encoding=encoding) as f:
        return f.read().strip()


@wraps(text)
def lines(*args: str, **kwargs: str) -> List[str]:
    return [y for x in text(*args, **kwargs).splitlines() for y in [x.strip()] if y]


@wraps(text)
def json(*args: str, **kwargs: str) -> Dict[str, Any]:
    import json as _json

    return _read_simple_dict(partial(_json.loads, text(*args, **kwargs)))


@wraps(text)
def yaml(*args: str, **kwargs: str) -> Dict[str, Any]:
    import yaml as _yaml

    return _read_simple_dict(partial(_yaml.safe_load, text(*args, **kwargs)))


@wraps(text)
def yaml_all(*args: str, **kwargs: str) -> List[Dict[str, Any]]:
    import yaml as _yaml

    def _yaml_all(txt: str) -> List[Dict[str, Any]]:
        return [_read_simple_dict(lambda y: y, y=x) for x in _yaml.safe_load_all(txt)]

    return _yaml_all(text(*args, **kwargs))


@wraps(text)
def toml(*args: str, **kwargs: str) -> Dict[str, Any]:
    try:
        import tomli as _toml
    except ImportError:
        import tomllib as _toml

    return _read_simple_dict(partial(_toml.loads, text(*args, **kwargs)))


@wraps(text)
def cfg(*args: str, **kwargs: str) -> Dict[str, Any]:
    from configparser import ConfigParser

    def _read_cfg(txt: str) -> Dict[str, Any]:
        cp = ConfigParser()
        cp.read_string(txt)
        return {x: dict(cp.items(x)) for x in cp.sections()}

    return _read_simple_dict(partial(_read_cfg, text(*args, **kwargs)))


@wraps(cfg)
def ini(*args: str, **kwargs: str) -> Dict[str, Any]:
    return cfg(*args, **kwargs)


@wraps(text)
def dotfile(*args: str, **kwargs: str) -> Dict[str, str]:
    from io import StringIO

    from dotenv import dotenv_values

    return _read_simple_dict(
        partial(dotenv_values, stream=StringIO(text(*args, **kwargs)))
    )


@wraps(dotfile)
def envfile(*args: str, **kwargs: str) -> Dict[str, str]:
    return dotfile(*args, **kwargs)


def _url(addr: str, **kwargs: Any) -> Any:
    import requests

    addr = kwargs.pop("url", addr)
    method: str = kwargs.pop("method", "GET")
    timeout: float = kwargs.pop("timeout", 10)
    resp: requests.Response = requests.request(
        method=method, url=addr, timeout=timeout, **kwargs
    )
    return resp

    # req = urllib.request.Request(url=addr, **kwargs)
    # with urllib.request.urlopen(req) as resp:
    #     return str(resp.read())


def url(addr: str, **kwargs: Any) -> str:
    resp_text: str = _url(addr=addr, **kwargs).text
    return resp_text


def url_dict(addr: str, **kwargs: Any) -> Dict[str, Any]:
    resp: Any = _url(addr=addr, **kwargs).json()
    resp_dict: Dict[str, Any] = _read_simple_dict(lambda: resp)
    return resp_dict
