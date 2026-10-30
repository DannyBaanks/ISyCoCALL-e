import math

import pytest

from isyco_calle.config import ConfigError, Settings


@pytest.mark.parametrize("base_url", ["", "http://example.test", "https://user:pass@example.test"])
def test_rejects_unsafe_base_urls(base_url):
    with pytest.raises(ConfigError):
        Settings("real-looking-key", calle_base_url=base_url).validate()


@pytest.mark.parametrize("timeout", [-1, 0, math.nan, math.inf])
def test_rejects_invalid_timeouts(timeout):
    with pytest.raises(ConfigError):
        Settings("real-looking-key", calle_timeout=timeout).validate()


def test_load_rejects_non_numeric_timeout():
    with pytest.raises(ConfigError):
        Settings.load({"CALLE_API_KEY": "real-looking-key", "CALLE_TIMEOUT": "later"})
