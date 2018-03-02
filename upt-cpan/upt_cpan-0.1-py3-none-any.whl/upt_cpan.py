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

    def parse(self, pkg_name):
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
        }
        return CPANPackage(pkg_name, version, **pkg_args)
