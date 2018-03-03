import re
from voluptuous import Schema
from voluptuous import Required, All, Length, Range, Invalid, Optional, Url, extra


# Common validation functions
def validate_ip_address(ip_address: str) -> str:
    if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip_address):
        raise Invalid("Not valid IP address format.")
    return ip_address


# Connection validation schemas
# Basic connection schema
ConnectionSchema = {Required('server'): All(Url)}


# Oauth connection schema
credentialsSchema = {
    Optional('grant_type', default='password'): All(str, Length(min=1)),
    Optional('scope', default='admembership'): All(str, Length(min=1)),
    Required('client_id'): All(str, Length(min=1)),
    Required('client_secret'): All(str, Length(min=1)),
    Required('username'): All(str, Length(min=1)),
    Required('password'): All(str, Length(min=1)),
    }

resource_serverSchema = {
    Required('url'): All(Url),
    Required('key', default='admembership'): All(str, Length(min=1))
    }

OauthClientSchema = ConnectionSchema.copy()
OauthClientSchema.update({
    Required('server'): All(str, Length(min=1)),
    Required('credentials'): All(dict, credentialsSchema),
    Optional('resource_server'): All(dict, resource_serverSchema)
    })

# Zookeeper connection schema
ZookeeperSchema = ConnectionSchema.copy()

__schemas = {'oauthclient': All(dict, {extra: All(dict, OauthClientSchema)}),
             'zookeeper': All(dict, {extra: ZookeeperSchema}),
            }


# Listen filed validator
listenSchema = {
    Required('address'): All(str, validate_ip_address),
    Required('port'): All(int, Range(min=1025, max=65535)),
    }


# Service validator
serviceSchema = Schema({
    Required('name'): All(str, Length(min=1)),
    Required('api_version'): All(str, Length(min=1)),
    Required('listen'): All(dict, listenSchema),
    Optional('debug', default=False): All(bool),
    Required('token_provider'): All(str, Length(min=1)),
    Required('connections'): All(dict, __schemas),
    })
