import os
from os.path import abspath, dirname, join, normpath, isfile
import numpy as np
import pandas as pd
import unittest

import mhkit.acoustics as acoustics


testdir = dirname(abspath(__file__))
plotdir = join(testdir, "plots")
isdir = os.path.isdir(plotdir)
if not isdir:
    os.mkdir(plotdir)
datadir = normpath(join(testdir, "..", "..", "..", "examples", "data", "acoustics"))


class TestIO(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        pass

    @classmethod
    def tearDownClass(self):
        pass

    def test_read_iclisten(self):
        file_name = join(datadir, "RBW_6661_20240601_053114.wav")
        td_orig = acoustics.io.read_iclisten(file_name)
        td_wrap = acoustics.io.read_hydrophone(
            file_name, peak_V=3, sensitivity=-177, start_time="2024-06-01T05:31:14"
        )
        td_volt = acoustics.io.read_iclisten(
            file_name, sensitivity=None, use_metadata=False
        )
        td_ovrrd = acoustics.io.read_iclisten(
            file_name, sensitivity=-180, use_metadata=False
        )
        td_ovrrd2 = acoustics.io.read_iclisten(
            file_name, sensitivity=-180, use_metadata=True
        )

        # Check time coordinate
        cc = np.array(
            [
                "2024-06-01T05:31:14.000000000",
                "2024-06-01T05:31:14.000001953",
                "2024-06-01T05:31:14.000003906",
                "2024-06-01T05:31:14.000005859",
                "2024-06-01T05:31:14.000007812",
            ],
            dtype="datetime64[ns]",
        )
        # Check data
        cd_orig = np.array([0.31546374, 0.30229832, 0.32229963, 0.3159701, 0.30356423])
        cd_volt = np.array([0.0004456, 0.00042701, 0.00045526, 0.00044632, 0.0004288])
        cd_ovrrd = np.array(
            [0.44560438, 0.42700773, 0.45526033, 0.44631963, 0.42879587]
        )

        np.testing.assert_allclose(td_orig.head().values, cd_orig, atol=1e-6)
        np.testing.assert_equal(td_orig["time"].head().values, cc)

        np.testing.assert_allclose(td_wrap.head().values, cd_orig, atol=1e-6)
        np.testing.assert_equal(td_wrap["time"].head().values, cc)

        np.testing.assert_allclose(td_volt.head().values, cd_volt, atol=1e-6)
        np.testing.assert_equal(td_volt["time"].head().values, cc)

        np.testing.assert_allclose(td_ovrrd.head().values, cd_ovrrd, atol=1e-6)
        np.testing.assert_equal(td_ovrrd["time"].head().values, cc)

        np.testing.assert_allclose(
            td_ovrrd.head().values, td_ovrrd2.head().values, atol=1e-6
        )

    def test_read_soundtrap(self):
        file_name = join(datadir, "6247.230204150508.wav")
        td_orig = acoustics.io.read_soundtrap(file_name, sensitivity=-177)
        td_wrap = acoustics.io.read_hydrophone(
            file_name, peak_V=1, sensitivity=-177, start_time="2023-02-04T15:05:08"
        )
        td_volt = acoustics.io.read_soundtrap(file_name, sensitivity=None)

        # Check time coordinate
        cc = np.array(
            [
                "2023-02-04T15:05:08.000000000",
                "2023-02-04T15:05:08.000010416",
                "2023-02-04T15:05:08.000020832",
                "2023-02-04T15:05:08.000031249",
                "2023-02-04T15:05:08.000041665",
            ],
            dtype="datetime64[ns]",
        )
        # Check data
        cd_orig = np.array([0.929006, 0.929006, 0.929006, 0.929006, 1.01542517])
        cd_volt = np.array([0.00131226, 0.00131226, 0.00131226, 0.00131226, 0.00143433])

        np.testing.assert_allclose(td_orig.head().values, cd_orig, atol=1e-6)
        np.testing.assert_equal(td_orig["time"].head().values, cc)

        np.testing.assert_allclose(td_wrap.head().values, cd_orig, atol=1e-6)
        np.testing.assert_equal(td_wrap["time"].head().values, cc)

        np.testing.assert_allclose(td_volt.head().values, cd_volt, atol=1e-6)
        np.testing.assert_equal(td_volt["time"].head().values, cc)

    def test_calibration(self):
        file_name = join(datadir, "6247.230204150508.wav")
        td_volt = acoustics.io.read_soundtrap(file_name, sensitivity=None)
        td_spsd = acoustics.sound_pressure_spectral_density(
            td_volt, td_volt.fs, window=1
        )

        # Run calibration
        cal_name = join(datadir, "6247_calibration.csv")
        calibration = pd.read_csv(cal_name, sep=",")
        calibration.index = calibration["Frequency"]
        calibration = calibration.to_xarray()
        fill_Sf = calibration["Analog Sensitivity"][-1].values

        # Apply calibration
        td_spsd = acoustics.apply_calibration(
            td_spsd, calibration["Analog Sensitivity"], fill_value=fill_Sf
        )

        # Check time coordinate
        cc = np.array(
            [
                "2023-02-04T15:05:08.499983310",
                "2023-02-04T15:05:09.499959707",
                "2023-02-04T15:05:10.499936580",
                "2023-02-04T15:05:11.499913454",
                "2023-02-04T15:05:12.499890089",
            ],
            dtype="datetime64[ns]",
        )

        cd_spsd = np.array(
            [
                [
                    6.63068204e-02,
                    3.81400273e-03,
                    9.28277032e-04,
                    3.86833846e-04,
                    2.31924928e-05,
                ],
                [
                    1.32674948e-01,
                    8.07329208e-03,
                    3.35305424e-04,
                    8.63341841e-05,
                    3.23737989e-04,
                ],
                [
                    1.37353862e-02,
                    1.03924150e-02,
                    5.24537532e-03,
                    1.18371618e-03,
                    5.28236923e-05,
                ],
                [
                    2.70499444e-03,
                    1.47833274e-04,
                    2.46503548e-04,
                    2.36905027e-04,
                    1.92069973e-04,
                ],
                [
                    6.80966653e-03,
                    2.33636493e-03,
                    3.21849897e-04,
                    9.13295549e-05,
                    3.50420384e-05,
                ],
            ]
        )

        np.testing.assert_allclose(td_spsd.head().values, cd_spsd, atol=1e-6)
        np.testing.assert_equal(td_spsd["time"].head().values, cc)

    def test_audio_export(self):
        file_name = join(datadir, "RBW_6661_20240601_053114.wav")
        P = acoustics.io.read_iclisten(file_name)
        acoustics.io.export_audio("sound1", P, gain=1)

        self.assertEqual(isfile("sound1.wav"), True)
        os.remove("sound1.wav")