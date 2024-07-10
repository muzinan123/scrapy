# -*- coding: utf-8 -*-
# @Author blackrat  wangmingbo@zhongan.io
# @Time 2020-03-25 16:02

import os
import platform
from config import ROOT_PATH


class PlatformNotSupportExceptin(Exception):

    def __str__(self):
        s = 'Not support this platform: {0}, {1}'.format(platform.machine(), platform.system())
        print(s)


class LangDetector(object):

    __enry_bin_map__ = {
        'x86_64': {
            'darwin': 'bin/enry_darwin_amd64/enry',
            'linux': 'bin/enry_linux_amd64/enry'
        }
    }

    def scan(self, target):

        bin_map = self.__enry_bin_map__.get(platform.machine(), None)
        if not bin_map:
            raise PlatformNotSupportExceptin()
        else:
            bin_path = bin_map.get(platform.system().lower(), None)
            if not bin_path:
                raise PlatformNotSupportExceptin()
            bin_path = os.path.join(ROOT_PATH, bin_path)
            # todo finish scan





