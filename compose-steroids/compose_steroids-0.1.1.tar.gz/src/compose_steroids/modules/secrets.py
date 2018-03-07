from .base import Base


class Secrets(Base):

    def run(self, compose):
        secrets = compose.setdefault('secrets', {})
        self.infer_secret_definitions(
            secrets,
            compose.get('services', {}),
        )

    def infer_secret_definitions(self, secrets, services):
        for name, service in services.items():
            for secret in service.get('secrets', []):
                if isinstance(secret, dict):
                    name = secret['source']
                else:
                    name = secret
                if name not in secrets:
                    secrets[name] = {
                        'external': True,
                    }
