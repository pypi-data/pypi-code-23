#
# Copyright 2014 OpenStack Foundation.  All rights reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from cryptography import x509
import six

import neutron_lbaas.common.exceptions as exceptions
import neutron_lbaas.common.tls_utils.cert_parser as cert_parser
from neutron_lbaas.tests import base


ALT_EXT_CRT = """-----BEGIN CERTIFICATE-----
MIIGqjCCBZKgAwIBAgIJAIApBg8slSSiMA0GCSqGSIb3DQEBBQUAMIGLMQswCQYD
VQQGEwJVUzEOMAwGA1UECAwFVGV4YXMxFDASBgNVBAcMC1NhbiBBbnRvbmlvMR4w
HAYDVQQKDBVPcGVuU3RhY2sgRXhwZXJpbWVudHMxFjAUBgNVBAsMDU5ldXRyb24g
TGJhYXMxHjAcBgNVBAMMFXd3dy5DTkZyb21TdWJqZWN0Lm9yZzAeFw0xNTA1MjEy
MDMzMjNaFw0yNTA1MTgyMDMzMjNaMIGLMQswCQYDVQQGEwJVUzEOMAwGA1UECAwF
VGV4YXMxFDASBgNVBAcMC1NhbiBBbnRvbmlvMR4wHAYDVQQKDBVPcGVuU3RhY2sg
RXhwZXJpbWVudHMxFjAUBgNVBAsMDU5ldXRyb24gTGJhYXMxHjAcBgNVBAMMFXd3
dy5DTkZyb21TdWJqZWN0Lm9yZzCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoC
ggEBALL1nmbDPUDps84i1sM3rhHrc+Dlu0N/wKQWKZFeiWUtF/pot19V3o0yXDps
g7W5RkLMTFkZEcnQpyGdpAGjTjzmNXMZw99EzxsmrR3l6hUEISifVbvEuftYZT6j
PxM5ML6WAjFNaBEZPWtZi8CgX5xdjdrDNndwyHob49n7Nc/h1kVqqBqMILabTqC6
yEcxS/B+DugVuuYbEdYYYElQUMfM+mUdULrSqIVl2n5AvvSFjWzWzfgPyp4QKn+f
7HVRT62bh/XjQ88n1tMYNAEqixRZTPgqY1LFl9VJVgRp9fdL6ttMurOR3C0STJ5q
CdKBL7LrpbY4u8dEragRC6YAyI8CAwEAAaOCAw0wggMJMAkGA1UdEwQCMAAwCwYD
VR0PBAQDAgXgMIIC7QYDVR0RBIIC5DCCAuCCGHd3dy5ob3N0RnJvbUROU05hbWUx
LmNvbYIYd3d3Lmhvc3RGcm9tRE5TTmFtZTIuY29tghh3d3cuaG9zdEZyb21ETlNO
YW1lMy5jb22CGHd3dy5ob3N0RnJvbUROU05hbWU0LmNvbYcECgECA4cQASNFZ4mr
ze/3s9WR5qLEgIYWaHR0cDovL3d3dy5leGFtcGxlLmNvbaSBjzCBjDELMAkGA1UE
BhMCVVMxDjAMBgNVBAgMBVRleGFzMRQwEgYDVQQHDAtTYW4gQW50b25pbzEeMBwG
A1UECgwVT3BlblN0YWNrIEV4cGVyaW1lbnRzMRYwFAYDVQQLDA1OZXV0cm9uIExi
YWFzMR8wHQYDVQQDDBZ3d3cuY25Gcm9tQWx0TmFtZTEub3JnpIGPMIGMMQswCQYD
VQQGEwJVUzEOMAwGA1UECAwFVGV4YXMxFDASBgNVBAcMC1NhbiBBbnRvbmlvMR4w
HAYDVQQKDBVPcGVuU3RhY2sgRXhwZXJpbWVudHMxFjAUBgNVBAsMDU5ldXRyb24g
TGJhYXMxHzAdBgNVBAMMFnd3dy5jbkZyb21BbHROYW1lMi5vcmekgY8wgYwxCzAJ
BgNVBAYTAlVTMQ4wDAYDVQQIDAVUZXhhczEUMBIGA1UEBwwLU2FuIEFudG9uaW8x
HjAcBgNVBAoMFU9wZW5TdGFjayBFeHBlcmltZW50czEWMBQGA1UECwwNTmV1dHJv
biBMYmFhczEfMB0GA1UEAwwWd3d3LmNuRnJvbUFsdE5hbWUzLm9yZ6SBjzCBjDEL
MAkGA1UEBhMCVVMxDjAMBgNVBAgMBVRleGFzMRQwEgYDVQQHDAtTYW4gQW50b25p
bzEeMBwGA1UECgwVT3BlblN0YWNrIEV4cGVyaW1lbnRzMRYwFAYDVQQLDA1OZXV0
cm9uIExiYWFzMR8wHQYDVQQDDBZ3d3cuY25Gcm9tQWx0TmFtZTQub3JnMA0GCSqG
SIb3DQEBBQUAA4IBAQCS6iDn6R3C+qJLZibaqrBSkM9yu5kwRsQ6lQ+DODvVYGWq
eGkkh5o2c6WbJlH44yF280+HvnJcuISD7epPHJN0vUM9+WMtXfEli9avFHgu2JxP
3P0ixK2kaJnqKQkSEdnA/v/eWP1Cd2v6rbKCIo9d2gSP0cnpdtlX9Zk3SzEh0V7s
RjSdfZoAvz0aAnpDHlTerLcz5T2aiRae2wSt/RLA3qDO1Ji05tWvQBmKuepxS6A1
tL4Drm+OCXJwTrE7ClTMCwcrZnLl4tI+Z+X3DV92WQB8ldST/QFjz1hgs/4zrADA
elu2c/X7MR4ObOjhDfaVGQ8kMhYf5hx69qyNDsGi
-----END CERTIFICATE-----
"""

SOME_OTHER_RSA_KEY = """
-----BEGIN RSA PRIVATE KEY-----
MIICWwIBAAKBgQDDnJL9dAdDpjoq4tksTJmdM0AjIHa7Y2yc8XwU7YkgrOR0m4Po
r7El0NwWf5i/LFudX1cOkfwemMIPwQ+67k0BVu/W3SR+g9ZzVKZtTBJnDoqMZ4RJ
jBk4gfwhnQYKPIQvdilDZReH3hFcBvPUkYWSHMn17FBTGmNzp2AnMdLpQQIDAQAB
AoGAIlew7tKaG+RpPfJJ0p84MQM4dXJTph6UiRFUiZASjSwNh/Ntu0JtRYhfu4t3
U8kD5KNCc4ppyy1ilMV+b4E6/3ydz6syMeJ7G24/PMU8d44zDgZXdM1pf5Nlosh1
BVv1Fvb0PBW2xs9VRlO6W62IWVtsZCGXYNayrXDiRZ50IGkCQQDkmOVEqffz3GeD
A+XWp9YrXeMqOmtPcrOuvMIO9DwrlXb8eNwvG5GxbuHGuZfOp01tiPyQrkxM0JzU
y8iD1pjrAkEA2w9topUzYS/NZt45OD9t5ZBVMfP15AwWRVv7V5uTksTqfZ9tFfh6
pN4oWe6xK/kgKAdE9hkjubGKQBjJSC27gwJAGZlRm1XZUXKuGMrX8yjKYALcjH8M
Q1JZ8shqhtgs4MiVEYLLTW8t6ou7NtDTwi2UCx8bAWyzWKrH1UCYzMK8TwJAMngU
fz+2ra5wuUF7l1ztudUN+8tEHH04aFRvzNhYIJljmPuxCz3LK87PJyEaCpKD+RTr
q3NRSsf/nRLY1NtMdwJAVKOdUCwZKGpGyOUZPRbZZAPlojIff2CxJ6E2Pr0RbShD
31icKmhIY+e2rP6v5W7hzTGge5PA0hRfCiwyd+zLoQ==
-----END RSA PRIVATE KEY-----
"""

ALT_EXT_CRT_KEY = """
-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAsvWeZsM9QOmzziLWwzeuEetz4OW7Q3/ApBYpkV6JZS0X+mi3
X1XejTJcOmyDtblGQsxMWRkRydCnIZ2kAaNOPOY1cxnD30TPGyatHeXqFQQhKJ9V
u8S5+1hlPqM/EzkwvpYCMU1oERk9a1mLwKBfnF2N2sM2d3DIehvj2fs1z+HWRWqo
GowgtptOoLrIRzFL8H4O6BW65hsR1hhgSVBQx8z6ZR1QutKohWXafkC+9IWNbNbN
+A/KnhAqf5/sdVFPrZuH9eNDzyfW0xg0ASqLFFlM+CpjUsWX1UlWBGn190vq20y6
s5HcLRJMnmoJ0oEvsuultji7x0StqBELpgDIjwIDAQABAoIBAC3DX6FZtfU+jgtd
n1vGhk3wzu4o8S0+ow2S2UhiS3JDCMmxM4s+ky26Phl2nGvBGDWGttNl9MWOBN80
x7bfgudR20M2yH70wp1n04c8vxJmvu/7ZtogYYrjvOg6qKuKyWtDQwZGjCErOiiU
eodku25qAhd6Khh7D9kh/q9EbSteYFXsqJiNrY4ul1+cROMZpHx63xY6AzPmkvSU
garkgY4rw9E71t7it2laWkRKVsd+kEjayritdEEliNMVFFtrGEgplYkmLxGf0HLi
ROFVMCLRW/P12JpXllFPrBb8rlPL4w1c/s+yStohT0K+o4FLXhsf/inxmfc9XnZX
dJm0k/ECgYEA47FpV1caMk+TNPfu318VCGRmjwpXdmkNaUiX2Uvs3xIKQ6KJmpo3
sj0YjQEmQVz8s6geStvU1LdPxgsWZfbDt31M6SNwylh82ABQF1bZyrcMRxM8bHhe
bhDITM1dAn6aROkS1cBpfR9NJOFD850lmJvBGR9ORVBGyucTKH5uXxkCgYEAyTU0
zQKW2aU3J7mTCC9cp+eSD3fubJpa3ML5XfQ8YNID4PsxWglNKPcOTC4yaSfxVmyk
S0WIQUazCstszQsvwy9YyHtpkMq+0lyCPvrYnmRV0zx5zT155V2zcEh/oj64eoee
W5kvJSs/x6vT+lEN0TDEJ2gKEaJuBt6JG6P04ecCgYBSNw1CbEEZSYJt7dhi74I4
tYgSvjk2mFgvW/b4j2HIaksqgNYO7QCPa2AiCfg2Qc09UcceYKJI7Kfxaq97wc6J
wsSyqglgBvONSw+gXcvmVpIoV9nJkO0H8SdiFAUxkWVC3KXgaMmuVE8WsgBHRsb8
g8EFwTgR7xqgyS8xv/U6gQKBgQCdUr/dSJgAx6EPq5degAHXu0ZGWAUR38MJ+F2Y
6/5FyhCEWoRlHP66+CmywTBjbnrSk5IG1PBL8ebOmu6QiJ2o5R1rbKvHLe/0dabV
bbfwaQ1+ZDvskZP9Fr3WHqnFh3shO2dDwcvOKTnuetj9UWEXXyUQltXAohubvWbB
OPqhowKBgB3t2oUSFJI8fSNQnQNkcespJTddr0oLEwgsIl4Q7rdFHLr+/c46svjJ
kPMtpfxDQvkgK2aWpS4OP0E2vSU/IfMEDmlypfKe2SaTtFehZSUwR4R1/ZhSL3iS
iMwJYgm98P27s4TEMdhlPNVJrj1FrD+4VrgpOsoM20EkZnTvel9s
-----END RSA PRIVATE KEY-----
"""

ENCRYPTED_PKCS8_CRT_KEY_PASSPHRASE = "test_passphrase"

ENCRYPTED_PKCS8_CRT_KEY = """-----BEGIN ENCRYPTED PRIVATE KEY-----
MIIE6TAbBgkqhkiG9w0BBQMwDgQIT04zko6pmJICAggABIIEyL/79sqzTQ7BsEjY
ao2Uhh3//mpNJfCDhjSZOmWL7s4+161cEqpxrfxo4bHH8fkZ60VZUQP8CjwwQUhP
4iwpv2bYbQwzlttZwTC6s28wh7FRtgVoVPTwvXJa6fl2zAjLtsjwLZ/556ez9xIJ
67hxkIK2EzGQaeEKI1+vVF5EKsgKiPEmgspOBxRPoVWTx49NooiakGnwaBoDyTob
8FMr8mF1EheNQ4kl1bPrl+csD7PPnfbWUdNVvMljEhS3cYamQDPEWyAzvaIr0rHh
/6h80L/G2+0fensrTspWJcjX+XDBwQPk+YMic0TJ3KvkC7p2iNJhjNrjhQ+APZWq
xYrjfcmdK0RaaoqN+1zeE1P2kWIJx9CQZVMeGhVzzcmPwJPDnJFpkU+8cgTWnUr/
Fh8YtDoDzLiAUcmV1Kk7LYtYPHuU8epuz5PYm49TbWzdS7PX5wqFAFmrVt5jysm4
D/Ox0r4KV1t7D/1gc1WRIu8oUXkIglCHWNpTyMK0kFPctAf/ua+DUFRE4eSx3rsX
ZKIymdF9v/WF1Ud0tsNeudQbVeXWS6UCR8m/rqe81W4npQm/uqUNla+6yaYUmHlk
tvw/m6pt+jKhn0XIRkMwHrTpIaMVvInMg0xpkRuc7Xj5A7vNnkypZRNZJHgy7WWC
6GpOCWJOltYaNy7tmAkSUHJ6kNjXK5a4fi30HknEaqKjFTQNGvcybulJ3MXUzds0
MJoTpvQfLzYQbMYZ/XRGND4lgeEbs29nWLPae8D5XlDeZQMin8EukPko8u8+YGbU
eWGOvDc+4/xrWrsq1i6R0uWq+Cyoql8oh0PNBlM04S7GAbu1pOD/tPcq/GNYcv/Q
vJcIz9KA3BNepq7tC8D88ggEvFjTsHKeW/OnuCxKducSna4Mq+GebU52tKjkLjFC
eLG4Vx0BY5xPH3gd7iyuAf7S+08BbinNZWjHLpdmR3vKK5YbLPiGSfcYQdClr6BK
9vNWH4TXmZMV+rWtfSeM/cbhCHwxT5Jx6N0OFAxOblQClWnUD79nGkEgn/GoY/Aj
FPNj8u2U/mJHgFHH3ClidYL9jJUvhGpTixB8nGgMjJ0wvFcp+5OysG3TsjqYkwR6
RRNBmM+iLEUFTrMZYb+edHvGJsMEMZ0qvjmZDsfDz6ax5M9zH/ORFcGplgIec8kj
I106+dqAVVrv1CrBf2N/pxV0OXVhgl6ECe/Ee1xYC2e2CiEgUnQtedu8ekgPgp73
tHcAiWMamLPTwXuL7jFtvWaQfkYBmrBdEx54+eZOfH/NgV3o8gbaWNHSxbfbwlXN
MvyJidZGkXU0DJtUUnO5i2S7ftKCdOzrrSA8HDTvxFUhxretYpF3NzPYpYkM7WJX
GM7bTMn37AWYqLZmdYYdjh1ZOH/wsM/3uxGBpyEyy4Urrr1ux7X1P0cL0O2P/72h
GRd499JLrRMrmmtQ4KrN7GCHdctvujhDP8zvmnaEyGVzg88XmDg50ZF3+8DmOOgX
EMZEYHO2Wi2uyFotFtZCuqoOJmGPPeGV8QrsRs82hnL1bcd6REUTWk0KsTt13lvF
WwMJugHFk5NQuse3P4Hh9smQrRrv1dvnpt7s4yKStKolXUaFWcXJvXVaDfR5266Y
p7cuYY1cAyI7gFfl5A==
-----END ENCRYPTED PRIVATE KEY-----
"""

UNENCRYPTED_PKCS8_CRT_KEY = """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCy9Z5mwz1A6bPO
ItbDN64R63Pg5btDf8CkFimRXollLRf6aLdfVd6NMlw6bIO1uUZCzExZGRHJ0Kch
naQBo0485jVzGcPfRM8bJq0d5eoVBCEon1W7xLn7WGU+oz8TOTC+lgIxTWgRGT1r
WYvAoF+cXY3awzZ3cMh6G+PZ+zXP4dZFaqgajCC2m06gushHMUvwfg7oFbrmGxHW
GGBJUFDHzPplHVC60qiFZdp+QL70hY1s1s34D8qeECp/n+x1UU+tm4f140PPJ9bT
GDQBKosUWUz4KmNSxZfVSVYEafX3S+rbTLqzkdwtEkyeagnSgS+y66W2OLvHRK2o
EQumAMiPAgMBAAECggEALcNfoVm19T6OC12fW8aGTfDO7ijxLT6jDZLZSGJLckMI
ybEziz6TLbo+GXaca8EYNYa202X0xY4E3zTHtt+C51HbQzbIfvTCnWfThzy/Ema+
7/tm2iBhiuO86Dqoq4rJa0NDBkaMISs6KJR6h2S7bmoCF3oqGHsP2SH+r0RtK15g
VeyomI2tji6XX5xE4xmkfHrfFjoDM+aS9JSBquSBjivD0TvW3uK3aVpaREpWx36Q
SNrKuK10QSWI0xUUW2sYSCmViSYvEZ/QcuJE4VUwItFb8/XYmleWUU+sFvyuU8vj
DVz+z7JK2iFPQr6jgUteGx/+KfGZ9z1edld0mbST8QKBgQDjsWlXVxoyT5M09+7f
XxUIZGaPCld2aQ1pSJfZS+zfEgpDoomamjeyPRiNASZBXPyzqB5K29TUt0/GCxZl
9sO3fUzpI3DKWHzYAFAXVtnKtwxHEzxseF5uEMhMzV0CfppE6RLVwGl9H00k4UPz
nSWYm8EZH05FUEbK5xMofm5fGQKBgQDJNTTNApbZpTcnuZMIL1yn55IPd+5smlrc
wvld9Dxg0gPg+zFaCU0o9w5MLjJpJ/FWbKRLRYhBRrMKy2zNCy/DL1jIe2mQyr7S
XII++tieZFXTPHnNPXnlXbNwSH+iPrh6h55bmS8lKz/Hq9P6UQ3RMMQnaAoRom4G
3okbo/Th5wKBgFI3DUJsQRlJgm3t2GLvgji1iBK+OTaYWC9b9viPYchqSyqA1g7t
AI9rYCIJ+DZBzT1Rxx5gokjsp/Fqr3vBzonCxLKqCWAG841LD6Bdy+ZWkihX2cmQ
7QfxJ2IUBTGRZULcpeBoya5UTxayAEdGxvyDwQXBOBHvGqDJLzG/9TqBAoGBAJ1S
v91ImADHoQ+rl16AAde7RkZYBRHfwwn4XZjr/kXKEIRahGUc/rr4KbLBMGNuetKT
kgbU8Evx5s6a7pCInajlHWtsq8ct7/R1ptVtt/BpDX5kO+yRk/0WvdYeqcWHeyE7
Z0PBy84pOe562P1RYRdfJRCW1cCiG5u9ZsE4+qGjAoGAHe3ahRIUkjx9I1CdA2Rx
6yklN12vSgsTCCwiXhDut0Ucuv79zjqy+MmQ8y2l/ENC+SArZpalLg4/QTa9JT8h
8wQOaXKl8p7ZJpO0V6FlJTBHhHX9mFIveJKIzAliCb3w/buzhMQx2GU81UmuPUWs
P7hWuCk6ygzbQSRmdO96X2w=
-----END PRIVATE KEY-----
"""

EXPECTED_IMD_SUBJS = ["IMD3", "IMD2", "IMD1"]

X509_IMDS = """Junk
-----BEGIN CERTIFICATE-----
MIIBhDCCAS6gAwIBAgIGAUo7hO/eMA0GCSqGSIb3DQEBCwUAMA8xDTALBgNVBAMT
BElNRDIwHhcNMTQxMjExMjI0MjU1WhcNMjUxMTIzMjI0MjU1WjAPMQ0wCwYDVQQD
EwRJTUQzMFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBAKHIPXo2pfD5dpnpVDVz4n43
zn3VYsjz/mgOZU0WIWjPA97mvulb7mwb4/LB4ijOMzHj9XfwP75GiOFxYFs8O80C
AwEAAaNwMG4wDwYDVR0TAQH/BAUwAwEB/zA8BgNVHSMENTAzgBS6rfnABCO3oHEz
NUUtov2hfXzfVaETpBEwDzENMAsGA1UEAxMESU1EMYIGAUo7hO/DMB0GA1UdDgQW
BBRiLW10LVJiFO/JOLsQFev0ToAcpzANBgkqhkiG9w0BAQsFAANBABtdF+89WuDi
TC0FqCocb7PWdTucaItD9Zn55G8KMd93eXrOE/FQDf1ScC+7j0jIHXjhnyu6k3NV
8el/x5gUHlc=
-----END CERTIFICATE-----
Junk should be ignored by x509 splitter
-----BEGIN CERTIFICATE-----
MIIBhDCCAS6gAwIBAgIGAUo7hO/DMA0GCSqGSIb3DQEBCwUAMA8xDTALBgNVBAMT
BElNRDEwHhcNMTQxMjExMjI0MjU1WhcNMjUxMTIzMjI0MjU1WjAPMQ0wCwYDVQQD
EwRJTUQyMFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBAJYHqnsisVKTlwVaCSa2wdrv
CeJJzqpEVV0RVgAAF6FXjX2Tioii+HkXMR9zFgpE1w4yD7iu9JDb8yTdNh+NxysC
AwEAAaNwMG4wDwYDVR0TAQH/BAUwAwEB/zA8BgNVHSMENTAzgBQt3KvN8ncGj4/s
if1+wdvIMCoiE6ETpBEwDzENMAsGA1UEAxMEcm9vdIIGAUo7hO+mMB0GA1UdDgQW
BBS6rfnABCO3oHEzNUUtov2hfXzfVTANBgkqhkiG9w0BAQsFAANBAIlJODvtmpok
eoRPOb81MFwPTTGaIqafebVWfBlR0lmW8IwLhsOUdsQqSzoeypS3SJUBpYT1Uu2v
zEDOmgdMsBY=
-----END CERTIFICATE-----
Junk should be thrown out like junk
-----BEGIN CERTIFICATE-----
MIIBfzCCASmgAwIBAgIGAUo7hO+mMA0GCSqGSIb3DQEBCwUAMA8xDTALBgNVBAMT
BHJvb3QwHhcNMTQxMjExMjI0MjU1WhcNMjUxMTIzMjI0MjU1WjAPMQ0wCwYDVQQD
EwRJTUQxMFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBAI+tSJxr60ogwXFmgqbLMW7K
3fkQnh9sZBi7Qo6AzUnfe/AhXoisib651fOxKXCbp57IgzLTv7O9ygq3I+5fQqsC
AwEAAaNrMGkwDwYDVR0TAQH/BAUwAwEB/zA3BgNVHSMEMDAugBR73ZKSpjbsz9tZ
URkvFwpIO7gB4KETpBEwDzENMAsGA1UEAxMEcm9vdIIBATAdBgNVHQ4EFgQULdyr
zfJ3Bo+P7In9fsHbyDAqIhMwDQYJKoZIhvcNAQELBQADQQBenkZ2k7RgZqgj+dxA
D7BF8MN1oUAOpyYqAjkGddSEuMyNmwtHKZI1dyQ0gBIQdiU9yAG2oTbUIK4msbBV
uJIQ
-----END CERTIFICATE-----"""


def _get_rsa_numbers(private_key, private_key_passphrase=None):
    """
    Grabs the private and public numbers as a dictionary
    from an RSA private key used for the dump_private_key test case

    :param private_key:
    :param private_key_passphrase:
    :returns: a dictionary with keys (p,q,e,d,t,e,n)
    """
    kw = {"private_key_passphrase": private_key_passphrase}
    pk = cert_parser._read_pyca_private_key(private_key, **kw)
    p = pk.private_numbers().p
    q = pk.private_numbers().q
    d = pk.private_numbers().d
    t = (p - 1) * (q - 1)
    e = pk.private_numbers().public_numbers.e
    n = pk.private_numbers().public_numbers.n  # should be p*q
    # Force a canonical representation for comparison algos
    # by swapping p and q if q is bigger
    if p < q:
        (p, q) = (q, p)
    return {"p": p, "q": q, "d": d, "t": t, "e": e, "n": n}


class TestTLSParseUtils(base.BaseTestCase):
    def test_alt_subject_name_parses(self):
        hosts = cert_parser.get_host_names(ALT_EXT_CRT)
        self.assertEqual('www.cnfromsubject.org', hosts['cn'])
        self.assertEqual('www.hostFromDNSName1.com', hosts['dns_names'][0])
        self.assertEqual('www.hostFromDNSName2.com', hosts['dns_names'][1])
        self.assertEqual('www.hostFromDNSName3.com', hosts['dns_names'][2])
        self.assertEqual('www.hostFromDNSName4.com', hosts['dns_names'][3])

    def test_x509_parses(self):
        self.assertRaises(exceptions.UnreadableCert,
                          cert_parser.validate_cert, "BAD CERT")
        self.assertTrue(cert_parser.validate_cert(six.u(ALT_EXT_CRT)))
        self.assertTrue(cert_parser.validate_cert(ALT_EXT_CRT))
        self.assertTrue(cert_parser.validate_cert(ALT_EXT_CRT,
                        private_key=UNENCRYPTED_PKCS8_CRT_KEY))

    def test_x509_parses_intermediates(self):
        # Should not throw error when parsing with intermediates
        cert_parser.validate_cert(ALT_EXT_CRT,
                                  UNENCRYPTED_PKCS8_CRT_KEY,
                                  intermediates=X509_IMDS)

    def test_read_private_key(self):
        self.assertRaises(exceptions.NeedsPassphrase,
                          cert_parser._read_privatekey,
                          ENCRYPTED_PKCS8_CRT_KEY)
        cert_parser._read_privatekey(
            str(ENCRYPTED_PKCS8_CRT_KEY),
            passphrase=ENCRYPTED_PKCS8_CRT_KEY_PASSPHRASE)

    def test_read_private_key_unicode(self):
        self.assertRaises(exceptions.NeedsPassphrase,
                          cert_parser._read_privatekey,
                          ENCRYPTED_PKCS8_CRT_KEY)
        cert_parser._read_privatekey(
            six.u(ENCRYPTED_PKCS8_CRT_KEY),
            passphrase=ENCRYPTED_PKCS8_CRT_KEY_PASSPHRASE)
        cert_parser._read_privatekey(
            ENCRYPTED_PKCS8_CRT_KEY,
            passphrase=six.u(ENCRYPTED_PKCS8_CRT_KEY_PASSPHRASE))

    def test_dump_private_key(self):
        self.assertRaises(exceptions.NeedsPassphrase,
                          cert_parser.dump_private_key,
                          ENCRYPTED_PKCS8_CRT_KEY)
        striped_rsa_key = _get_rsa_numbers(
            UNENCRYPTED_PKCS8_CRT_KEY)
        decrypted_rsa_key = _get_rsa_numbers(
            cert_parser.dump_private_key(ENCRYPTED_PKCS8_CRT_KEY,
                                         ENCRYPTED_PKCS8_CRT_KEY_PASSPHRASE))

        self.assertEqual(striped_rsa_key, decrypted_rsa_key)
        self.assertIsNot(ENCRYPTED_PKCS8_CRT_KEY,
                         cert_parser.dump_private_key(
                             ENCRYPTED_PKCS8_CRT_KEY,
                             ENCRYPTED_PKCS8_CRT_KEY_PASSPHRASE))

    def test_validate_cert_and_key_match(self):
        self.assertTrue(cert_parser.validate_cert(ALT_EXT_CRT,
                                                  private_key=ALT_EXT_CRT_KEY))
        self.assertRaises(exceptions.MisMatchedKey,
                          cert_parser.validate_cert,
                          ALT_EXT_CRT, private_key=SOME_OTHER_RSA_KEY)

    def test_split_x509s(self):
        imds = []
        for x509Pem in cert_parser._split_x509s(X509_IMDS):
            imds.append(cert_parser._get_x509_from_pem_bytes(x509Pem))

        for i in range(0, len(imds)):
            self.assertEqual(EXPECTED_IMD_SUBJS[i],
                             imds[i].subject.get_attributes_for_oid(
                                 x509.OID_COMMON_NAME)[0].value)
