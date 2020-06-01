
"""
diagnose and resolve problems with USAXS tunable motors

    RE(m1.tuner.tune())
    RE(m1.tuner.tune(width=.15, num=13))
    RE(m1.tuner.multi_pass_tune(num=6))
"""

__all__ = [
    'noisy', 
    'm1',
    'shutter',
    'calcs',
    ]

from ..session_logs import logger
logger.info(__file__)

from apstools.devices import setup_lorentzian_swait
from apstools.devices import SimulatedApsPssShutterWithStatus
from apstools.plans import TuneAxis
from apstools.synApps import UserCalcsDevice
from bluesky import plan_stubs as bps
import numpy as np
from ophyd import EpicsSignalRO

from .usaxs_sim_local import UsaxsMotorTunable


shutter = SimulatedApsPssShutterWithStatus(
    name="shutter", labels=("shutters",))
shutter.delay_s = 0.05 # shutter needs short recovery time after moving

m1 = UsaxsMotorTunable("sky:m1", name="m1", labels=("motors",))

# demo: use swait records to make "noisy" detector signals
calcs = UserCalcsDevice("sky:", name="calcs")
calcs.enable.put(1)

noisy = EpicsSignalRO(
    'sky:userCalc1', name='noisy', labels=("detectors",))

setup_lorentzian_swait(
    calcs.calc1,
    m1.user_readback,
    center = 2*np.random.random() - 1,
    width = 0.015 * np.random.random(),
    scale = 10000 * (9 + np.random.random()),
    noise=0.05,
)

def hook_pre_tune_m1():
    yield from bps.mv(shutter, "open")
def hook_post_tune_m1():
    yield from bps.mv(shutter, "close")

m1.pre_tune_method = hook_pre_tune_m1
m1.post_tune_method = hook_post_tune_m1

# m1.tuner = UsaxsTuneAxis([noisy], m1)
m1.tuner = TuneAxis([noisy], m1)
m1.tuner.peak_factor = 2.5
