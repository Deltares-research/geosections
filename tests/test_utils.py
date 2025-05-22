import numpy as np
import pytest
from numpy.testing import assert_array_almost_equal

from geosections import utils


@pytest.mark.unittest
def test_min_max_scaler():
    array = np.array([1, 2, 3, 4, 5])
    scaled_array = utils.min_max_scaler(array)
    expected_scaled_array = np.array([0.0, 0.25, 0.5, 0.75, 1.0])
    assert_array_almost_equal(scaled_array, expected_scaled_array)

    max_ = 10
    scaled_array_with_max = utils.min_max_scaler(array, max_)
    expected_scaled_array_with_max = np.array(
        [0.0, 0.11111111, 0.22222222, 0.33333333, 0.44444444]
    )
    assert_array_almost_equal(scaled_array_with_max, expected_scaled_array_with_max)
