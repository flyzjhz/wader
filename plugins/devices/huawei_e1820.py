# -*- coding: utf-8 -*-
# Copyright (C) 2011       Vodafone España, S.A.
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

from twisted.internet import reactor
from twisted.internet.task import deferLater

from wader.common import consts
from core.hardware.base import build_band_dict
from core.hardware.huawei import (HuaweiWCDMADevicePlugin,
                                          HuaweiWCDMACustomizer,
                                          HuaweiWCDMAWrapper,
                                          HUAWEI_BAND_DICT)


class HuaweiE1820Wrapper(HuaweiWCDMAWrapper):
    """
    :class:`~core.hardware.huawei.HuaweiWCDMAWrapper` for the E1820
    """

    def check_pin(self):
        """
        Returns the SIM's auth state

        :raise SimPinRequired: Raised if SIM PIN is required
        :raise SimPukRequired: Raised if SIM PUK is required
        :raise SimPuk2Required: Raised if SIM PUK2 is required
        """
        # XXX: this device needs to be enabled before pin can be checked

        d = self.get_radio_status()

        def get_radio_status_cb(status):
            if status != 1:
                self.send_at('AT+CFUN=1')

                # delay here 2 secs, or we perhaps we should wait for ^SRVST:1
                return deferLater(reactor, 2, lambda: None)

        d.addCallback(get_radio_status_cb)
        d.addCallback(lambda x: super(HuaweiE1820Wrapper, self).check_pin())

        return d

    def send_ussd(self, ussd):
        return self._send_ussd_old_mode(ussd)


class HuaweiE1820Customizer(HuaweiWCDMACustomizer):
    """
    :class:`~core.hardware.huawei.HuaweiWCDMACustomizer` for the E1820
    """
    wrapper_klass = HuaweiE1820Wrapper

    # GSM/GPRS/EDGE 850/900/1800/1900 MHz
    # HSDPA/UMTS 2100 MHz

    band_dict = build_band_dict(
                  HUAWEI_BAND_DICT,
                  [consts.MM_NETWORK_BAND_ANY,

                   consts.MM_NETWORK_BAND_G850,
                   consts.MM_NETWORK_BAND_EGSM,
                   consts.MM_NETWORK_BAND_DCS,
                   consts.MM_NETWORK_BAND_PCS,

                   consts.MM_NETWORK_BAND_U2100])


class HuaweiE1820(HuaweiWCDMADevicePlugin):
    """
    :class:`~core.plugin.DevicePlugin` for Huawei's E1820
    """
    name = "Huawei E1820"
    version = "0.1"
    author = u"Andrew Bird"
    custom = HuaweiE1820Customizer()

    __remote_name__ = "E1820"

    __properties__ = {
        'ID_VENDOR_ID': [0x12d1],
        'ID_MODEL_ID': [0x14ac],
    }

    conntype = consts.WADER_CONNTYPE_USB

huaweie1820 = HuaweiE1820()
