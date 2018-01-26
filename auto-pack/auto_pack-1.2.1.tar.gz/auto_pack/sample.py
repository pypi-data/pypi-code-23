#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import aliyun_oss_helper
if __name__ == "__main__":
    aliyun_oss_helper.uploadToAliyun(sys.argv[1:])
