import shlex
import sys
from typing import List, Mapping, NoReturn, Optional, Union

_ERROR_MESSAGE_FILENAME = "error-message.txt"
_ConfigSettings = Optional[Mapping[str, Optional[Union[str, List[str]]]]]


def _arbitrary_args(config_settings: _ConfigSettings) -> List[str]:
    cfg = config_settings or {}
    opts = cfg.get("--build-option") or []
    return shlex.split(opts) if isinstance(opts, str) else opts


def get_requires_for_build_sdist(config_settings: _ConfigSettings = None) -> List[str]:
    return ["setuptools>=64"]


def build_sdist(sdist_directory: str, config_settings: _ConfigSettings = None) -> str:
    from setuptools import build_meta

    try:
        return build_meta._BACKEND._build_with_temp_dir(
            ["sdist", "--formats", "gztar"],
            ".tar.gz",
            sdist_directory,
            config_settings,
            _arbitrary_args(config_settings),
        )
    except BaseException:
        print(sys.argv)
        raise


def build_wheel(
    wheel_directory: str,
    config_settings: _ConfigSettings = None,
    metadata_directory: Optional[str] = None,
) -> NoReturn:
    with open(_ERROR_MESSAGE_FILENAME) as fp:
        print(fp.read(), file=sys.stderr)
    raise SystemExit(1)
