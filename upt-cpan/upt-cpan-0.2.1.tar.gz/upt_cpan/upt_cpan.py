# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
import requests
import upt


class CPANPackage(upt.Package):
    pass


class CPANFrontend(upt.Frontend):
    name = 'cpan'

    def _get_homepage(self, json_resources):
        homepage = json_resources.get('homepage')
        if homepage is None:
            for kind in ('bugtracker', 'repository'):
                d = json_resources.get(kind, {})
                homepage = d.get('web')
                if homepage is not None:
                    break
        return homepage

    def _get_licenses(self, licenses):
        # List taken from https://metacpan.org/pod/CPAN::Meta::Spec#license .
        # Not included here:
        # - gpl_1: deprecated for ages
        # - ssleay: not even listed on https://spdx.org/licenses/
        # - open_source: not a real license
        # - restricte: not a real license
        # - unrestricte: not a real license
        # - unknown: not a real license
        metacpan_licenses = {
            'agpl_3':
                upt.licenses.GNUAfferoGeneralPublicLicenseThreeDotZeroPlus,
            'apache_1_1': upt.licenses.ApacheLicenseOneDotOne,
            'apache_2_0': upt.licenses.ApacheLicenseTwoDotZero,
            'artistic_1': upt.licenses.ArtisticLicenseOneDotZero,
            'artistic_2': upt.licenses.ApacheLicenseTwoDotZero,
            'bsd': upt.licenses.BSDThreeClauseLicense,
            'freebsd': upt.licenses.BSDTwoClauseLicense,
            'gfdl_1_2': upt.licenses.GNUFreeDocumentationLicenseOneDotTwo,
            'gfdl_1_3': upt.licenses.GNUFreeDocumentationLicenseOneDotThree,
            'gpl_2': upt.licenses.GNUGeneralPublicLicenseTwo,
            'gpl_3': upt.licenses.GNUGeneralPublicLicenseThree,
            'lgpl_2_1': upt.licenses.GNULesserGeneralPublicLicenseTwoDotOne,
            'lgpl_3_0': upt.licenses.GNULesserGeneralPublicLicenseThreeDotZero,
            'mit': upt.licenses.MITLicense,
            'mozilla_1_0': upt.licenses.MozillaPublicLicenseOneDotZero,
            'mozilla_1_1': upt.licenses.MozillaPublicLicenseOneDotOne,
            'openssl': upt.licenses.OpenSSLLicense,
            'perl_5': upt.licenses.PerlLicense,
            'qpl_1_0': upt.licenses.QPublicLicenseOneDotZero,
            'sun': upt.licenses.SunIndustryStandardsSourceLicenceOneDotOne,
            'zlib': upt.licenses.ZlibLicense,
        }

        return [metacpan_licenses.get(l, upt.licenses.UnknownLicense)()
                for l in licenses]

    def parse(self, pkg_name):
        # The following document https://metacpan.org/pod/CPAN::Meta::Spec
        # is quite useful to understand the JSON we get.
        release_name = pkg_name.replace('::', '-')
        url = f'https://fastapi.metacpan.org/v1/release/{release_name}'
        r = requests.get(url)
        if not r.ok:
            raise upt.InvalidPackageNameError(self.name, pkg_name)
        json = r.json()

        metadata = json.get('metadata', {})
        version = metadata.get('version', '')
        homepage = self._get_homepage(json.get('resources', {}))

        try:
            download_urls = [json['download_url']]
        except KeyError:
            download_urls = []

        pkg_args = {
            'summary': metadata.get('abstract', ''),
            'homepage': homepage,
            'download_urls': download_urls,
            'licenses': self._get_licenses(json.get('license', [])),
        }
        return CPANPackage(pkg_name, version, **pkg_args)
