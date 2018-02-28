#python 2x compatibility
try:
    from vault_gatekeeper_client.vault_gatekeeper_client import *
except ImportError:
    from vault_gatekeeper_client import *
