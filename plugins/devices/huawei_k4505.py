# -*- coding: utf-8 -*-
# Copyright (C) 2006-2011  Vodafone España, S.A.
# Author:  Andrew Bird
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from twisted.internet import defer, reactor
from twisted.internet.task import deferLater

from wader.common import consts
from core.hardware.base import build_band_dict
from core.hardware.huawei import (HuaweiWCDMADevicePlugin,
                                          HuaweiWCDMACustomizer,
                                          HuaweiWCDMAWrapper,
                                          HUAWEI_BAND_DICT)


class HuaweiK4505Wrapper(HuaweiWCDMAWrapper):
    """
    :class:`~core.hardware.huawei.HuaweiWCDMAWrapper` for the K4505
    """

    def enable_radio(self, enable):
        """
        Enables the radio according to ``enable``

        It will not enable it if it's already enabled and viceversa
        """

        def check_if_necessary(status):
            if (status == 1 and enable) or (status == 0 and not enable):
                return defer.succeed('OK')

            d = super(HuaweiK4505Wrapper, self).enable_radio(enable)
            d.addCallback(lambda x: deferLater(reactor, 5, lambda: x))
            return d

        d = self.get_radio_status()
        d.addCallback(check_if_necessary)
        return d

    def send_ussd(self, ussd):
        return self._send_ussd_ucs2_mode(ussd)


class HuaweiK4505Customizer(HuaweiWCDMACustomizer):
    """
    :class:`~core.hardware.huawei.HuaweiWCDMACustomizer` for the K4505
    """
    wrapper_klass = HuaweiK4505Wrapper

    # GSM/GPRS/EDGE 850/900/1800/1900 MHz
    # HSDPA/UMTS 2100/900 MHz
    band_dict = build_band_dict(
                  HUAWEI_BAND_DICT,
                  [consts.MM_NETWORK_BAND_ANY,

                   consts.MM_NETWORK_BAND_G850,
                   consts.MM_NETWORK_BAND_EGSM,
                   consts.MM_NETWORK_BAND_DCS,
                   consts.MM_NETWORK_BAND_PCS,

#                   consts.MM_NETWORK_BAND_U900, # waiting for docs
                   consts.MM_NETWORK_BAND_U2100])


class HuaweiK4505(HuaweiWCDMADevicePlugin):
    """
    :class:`~core.plugin.DevicePlugin` for Huawei's Vodafone K4505
    """
    name = "Huawei K4505"
    version = "0.1"
    author = u"Andrew Bird"
    custom = HuaweiK4505Customizer()
    quirks = {
        'needs_enable_before_pin_check': True,
    }

    __remote_name__ = "K4505"

    __properties__ = {
        'ID_VENDOR_ID': [0x12d1],
        'ID_MODEL_ID': [0x1464],
    }

    conntype = consts.WADER_CONNTYPE_USB

huaweik4505 = HuaweiK4505()
