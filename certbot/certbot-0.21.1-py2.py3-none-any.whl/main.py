"""Certbot main entry point."""
from __future__ import print_function
import functools
import logging.handlers
import os
import sys
import warnings

import configobj
import josepy as jose
import zope.component

from acme import errors as acme_errors

import certbot

from certbot import account
from certbot import cert_manager
from certbot import cli
from certbot import client
from certbot import configuration
from certbot import constants
from certbot import crypto_util
from certbot import eff
from certbot import errors
from certbot import hooks
from certbot import interfaces
from certbot import log
from certbot import renewal
from certbot import reporter
from certbot import storage
from certbot import util

from certbot.display import util as display_util, ops as display_ops
from certbot.plugins import disco as plugins_disco
from certbot.plugins import selection as plug_sel


USER_CANCELLED = ("User chose to cancel the operation and may "
                  "reinvoke the client.")


logger = logging.getLogger(__name__)


def _suggest_donation_if_appropriate(config):
    """Potentially suggest a donation to support Certbot.

    :param config: Configuration object
    :type config: interfaces.IConfig

    :returns: `None`
    :rtype: None

    """
    assert config.verb != "renew"
    if config.staging:
        # --dry-run implies --staging
        return
    reporter_util = zope.component.getUtility(interfaces.IReporter)
    msg = ("If you like Certbot, please consider supporting our work by:\n\n"
           "Donating to ISRG / Let's Encrypt:   https://letsencrypt.org/donate\n"
           "Donating to EFF:                    https://eff.org/donate-le\n\n")
    reporter_util.add_message(msg, reporter_util.LOW_PRIORITY)

def _report_successful_dry_run(config):
    """Reports on successful dry run

    :param config: Configuration object
    :type config: interfaces.IConfig

    :returns: `None`
    :rtype: None

    """
    reporter_util = zope.component.getUtility(interfaces.IReporter)
    assert config.verb != "renew"
    reporter_util.add_message("The dry run was successful.",
                              reporter_util.HIGH_PRIORITY, on_crash=False)


def _get_and_save_cert(le_client, config, domains=None, certname=None, lineage=None):
    """Authenticate and enroll certificate.

    This method finds the relevant lineage, figures out what to do with it,
    then performs that action. Includes calls to hooks, various reports,
    checks, and requests for user input.

    :param config: Configuration object
    :type config: interfaces.IConfig

    :param domains: List of domain names to get a certificate. Defaults to `None`
    :type domains: `list` of `str`

    :param certname: Name of new certificate. Defaults to `None`
    :type certname: str

    :param lineage: Certificate lineage object. Defaults to `None`
    :type lineage: storage.RenewableCert

    :returns: the issued certificate or `None` if doing a dry run
    :rtype: storage.RenewableCert or None

    :raises errors.Error: if certificate could not be obtained

    """
    hooks.pre_hook(config)
    try:
        if lineage is not None:
            # Renewal, where we already know the specific lineage we're
            # interested in
            logger.info("Renewing an existing certificate")
            renewal.renew_cert(config, domains, le_client, lineage)
        else:
            # TREAT AS NEW REQUEST
            assert domains is not None
            logger.info("Obtaining a new certificate")
            lineage = le_client.obtain_and_enroll_certificate(domains, certname)
            if lineage is False:
                raise errors.Error("Certificate could not be obtained")
            elif lineage is not None:
                hooks.deploy_hook(config, lineage.names(), lineage.live_dir)
    finally:
        hooks.post_hook(config)

    return lineage


def _handle_subset_cert_request(config, domains, cert):
    """Figure out what to do if a previous cert had a subset of the names now requested

    :param config: Configuration object
    :type config: interfaces.IConfig

    :param domains: List of domain names
    :type domains: `list` of `str`

    :param cert: Certificate object
    :type cert: storage.RenewableCert

    :returns: Tuple of (str action, cert_or_None) as per _find_lineage_for_domains_and_certname
              action can be: "newcert" | "renew" | "reinstall"
    :rtype: `tuple` of `str`

    """
    existing = ", ".join(cert.names())
    question = (
        "You have an existing certificate that contains a portion of "
        "the domains you requested (ref: {0}){br}{br}It contains these "
        "names: {1}{br}{br}You requested these names for the new "
        "certificate: {2}.{br}{br}Do you want to expand and replace this existing "
        "certificate with the new certificate?"
    ).format(cert.configfile.filename,
             existing,
             ", ".join(domains),
             br=os.linesep)
    if config.expand or config.renew_by_default or zope.component.getUtility(
            interfaces.IDisplay).yesno(question, "Expand", "Cancel",
                                       cli_flag="--expand",
                                       force_interactive=True):
        return "renew", cert
    else:
        reporter_util = zope.component.getUtility(interfaces.IReporter)
        reporter_util.add_message(
            "To obtain a new certificate that contains these names without "
            "replacing your existing certificate for {0}, you must use the "
            "--duplicate option.{br}{br}"
            "For example:{br}{br}{1} --duplicate {2}".format(
                existing,
                sys.argv[0], " ".join(sys.argv[1:]),
                br=os.linesep
            ),
            reporter_util.HIGH_PRIORITY)
        raise errors.Error(USER_CANCELLED)


def _handle_identical_cert_request(config, lineage):
    """Figure out what to do if a lineage has the same names as a previously obtained one

    :param config: Configuration object
    :type config: interfaces.IConfig

    :param lineage: Certificate lineage object
    :type lineage: storage.RenewableCert

    :returns: Tuple of (str action, cert_or_None) as per _find_lineage_for_domains_and_certname
              action can be: "newcert" | "renew" | "reinstall"
    :rtype: `tuple` of `str`

    """
    if not lineage.ensure_deployed():
        return "reinstall", lineage
    if renewal.should_renew(config, lineage):
        return "renew", lineage
    if config.reinstall:
        # Set with --reinstall, force an identical certificate to be
        # reinstalled without further prompting.
        return "reinstall", lineage
    question = (
        "You have an existing certificate that has exactly the same "
        "domains or certificate name you requested and isn't close to expiry."
        "{br}(ref: {0}){br}{br}What would you like to do?"
    ).format(lineage.configfile.filename, br=os.linesep)

    if config.verb == "run":
        keep_opt = "Attempt to reinstall this existing certificate"
    elif config.verb == "certonly":
        keep_opt = "Keep the existing certificate for now"
    choices = [keep_opt,
               "Renew & replace the cert (limit ~5 per 7 days)"]

    display = zope.component.getUtility(interfaces.IDisplay)
    response = display.menu(question, choices,
                            default=0, force_interactive=True)
    if response[0] == display_util.CANCEL:
        # TODO: Add notification related to command-line options for
        #       skipping the menu for this case.
        raise errors.Error(
            "Operation canceled. You may re-run the client.")
    elif response[1] == 0:
        return "reinstall", lineage
    elif response[1] == 1:
        return "renew", lineage
    else:
        assert False, "This is impossible"

def _find_lineage_for_domains(config, domains):
    """Determine whether there are duplicated names and how to handle
    them (renew, reinstall, newcert, or raising an error to stop
    the client run if the user chooses to cancel the operation when
    prompted).

    :param config: Configuration object
    :type config: interfaces.IConfig

    :param domains: List of domain names
    :type domains: `list` of `str`

    :returns: Two-element tuple containing desired new-certificate behavior as
              a string token ("reinstall", "renew", or "newcert"), plus either
              a RenewableCert instance or `None` if renewal shouldn't occur.
    :rtype: `tuple` of `str` and :class:`storage.RenewableCert` or `None`

    :raises errors.Error: If the user would like to rerun the client again.

    """
    # Considering the possibility that the requested certificate is
    # related to an existing certificate.  (config.duplicate, which
    # is set with --duplicate, skips all of this logic and forces any
    # kind of certificate to be obtained with renewal = False.)
    if config.duplicate:
        return "newcert", None
    # TODO: Also address superset case
    ident_names_cert, subset_names_cert = cert_manager.find_duplicative_certs(config, domains)
    # XXX ^ schoen is not sure whether that correctly reads the systemwide
    # configuration file.
    if ident_names_cert is None and subset_names_cert is None:
        return "newcert", None

    if ident_names_cert is not None:
        return _handle_identical_cert_request(config, ident_names_cert)
    elif subset_names_cert is not None:
        return _handle_subset_cert_request(config, domains, subset_names_cert)

def _find_cert(config, domains, certname):
    """Finds an existing certificate object given domains and/or a certificate name.

    :param config: Configuration object
    :type config: interfaces.IConfig

    :param domains: List of domain names
    :type domains: `list` of `str`

    :param certname: Name of certificate
    :type certname: str

    :returns: Two-element tuple of a boolean that indicates if this function should be
              followed by a call to fetch a certificate from the server, and either a
              RenewableCert instance or None.
    :rtype: `tuple` of `bool` and :class:`storage.RenewableCert` or `None`

    """
    action, lineage = _find_lineage_for_domains_and_certname(config, domains, certname)
    if action == "reinstall":
        logger.info("Keeping the existing certificate")
    return (action != "reinstall"), lineage

def _find_lineage_for_domains_and_certname(config, domains, certname):
    """Find appropriate lineage based on given domains and/or certname.

    :param config: Configuration object
    :type config: interfaces.IConfig

    :param domains: List of domain names
    :type domains: `list` of `str`

    :param certname: Name of certificate
    :type certname: str

    :returns: Two-element tuple containing desired new-certificate behavior as
              a string token ("reinstall", "renew", or "newcert"), plus either
              a RenewableCert instance or None if renewal should not occur.

    :rtype: `tuple` of `str` and :class:`storage.RenewableCert` or `None`

    :raises errors.Error: If the user would like to rerun the client again.

    """
    if not certname:
        return _find_lineage_for_domains(config, domains)
    else:
        lineage = cert_manager.lineage_for_certname(config, certname)
        if lineage:
            if domains:
                if set(cert_manager.domains_for_certname(config, certname)) != set(domains):
                    _ask_user_to_confirm_new_names(config, domains, certname,
                        lineage.names()) # raises if no
                    return "renew", lineage
            # unnecessarily specified domains or no domains specified
            return _handle_identical_cert_request(config, lineage)
        else:
            if domains:
                return "newcert", None
            else:
                raise errors.ConfigurationError("No certificate with name {0} found. "
                    "Use -d to specify domains, or run certbot --certificates to see "
                    "possible certificate names.".format(certname))

def _get_added_removed(after, before):
    """Get lists of items removed from `before`
    and a lists of items added to `after`
    """
    added = list(set(after) - set(before))
    removed = list(set(before) - set(after))
    added.sort()
    removed.sort()
    return added, removed

def _format_list(character, strings):
    """Format list with given character
    """
    formatted = "{br}{ch} " + "{br}{ch} ".join(strings)
    return formatted.format(
        ch=character,
        br=os.linesep
    )

def _ask_user_to_confirm_new_names(config, new_domains, certname, old_domains):
    """Ask user to confirm update cert certname to contain new_domains.

    :param config: Configuration object
    :type config: interfaces.IConfig

    :param new_domains: List of new domain names
    :type new_domains: `list` of `str`

    :param certname: Name of certificate
    :type certname: str

    :param old_domains: List of old domain names
    :type old_domains: `list` of `str`

    :returns: None
    :rtype: None

    :raises errors.ConfigurationError: if cert name and domains mismatch

    """
    if config.renew_with_new_domains:
        return

    added, removed = _get_added_removed(new_domains, old_domains)

    msg = ("You are updating certificate {0} to include new domain(s): {1}{br}{br}"
           "You are also removing previously included domain(s): {2}{br}{br}"
           "Did you intend to make this change?".format(
               certname,
               _format_list("+", added),
               _format_list("-", removed),
               br=os.linesep))
    obj = zope.component.getUtility(interfaces.IDisplay)
    if not obj.yesno(msg, "Update cert", "Cancel", default=True):
        raise errors.ConfigurationError("Specified mismatched cert name and domains.")

def _find_domains_or_certname(config, installer):
    """Retrieve domains and certname from config or user input.

    :param config: Configuration object
    :type config: interfaces.IConfig

    :param installer: Installer object
    :type installer: interfaces.IInstaller


    :returns: Two-part tuple of domains and certname
    :rtype: `tuple` of list of `str` and `str`

    :raises errors.Error: Usage message, if parameters are not used correctly

    """
    domains = None
    certname = config.certname
    # first, try to get domains from the config
    if config.domains:
        domains = config.domains
    # if we can't do that but we have a certname, get the domains
    # with that certname
    elif certname:
        domains = cert_manager.domains_for_certname(config, certname)

    # that certname might not have existed, or there was a problem.
    # try to get domains from the user.
    if not domains:
        domains = display_ops.choose_names(installer)

    if not domains and not certname:
        raise errors.Error("Please specify --domains, or --installer that "
                           "will help in domain names autodiscovery, or "
                           "--cert-name for an existing certificate name.")

    return domains, certname


def _report_new_cert(config, cert_path, fullchain_path, key_path=None):
    """Reports the creation of a new certificate to the user.

    :param cert_path: path to certificate
    :type cert_path: str

    :param fullchain_path: path to full chain
    :type fullchain_path: str

    :param key_path: path to private key, if available
    :type key_path: str

    :returns: `None`
    :rtype: None

    """
    if config.dry_run:
        _report_successful_dry_run(config)
        return

    assert cert_path and fullchain_path, "No certificates saved to report."

    expiry = crypto_util.notAfter(cert_path).date()
    reporter_util = zope.component.getUtility(interfaces.IReporter)
    # Print the path to fullchain.pem because that's what modern webservers
    # (Nginx and Apache2.4) will want.

    verbswitch = ' with the "certonly" option' if config.verb == "run" else ""
    privkey_statement = 'Your key file has been saved at:{br}{0}{br}'.format(
            key_path, br=os.linesep) if key_path else ""
    # XXX Perhaps one day we could detect the presence of known old webservers
    # and say something more informative here.
    msg = ('Congratulations! Your certificate and chain have been saved at:{br}'
           '{0}{br}{1}'
           'Your cert will expire on {2}. To obtain a new or tweaked version of this '
           'certificate in the future, simply run {3} again{4}. '
           'To non-interactively renew *all* of your certificates, run "{3} renew"'
           .format(fullchain_path, privkey_statement, expiry, cli.cli_command, verbswitch,
               br=os.linesep))
    reporter_util.add_message(msg, reporter_util.MEDIUM_PRIORITY)


def _determine_account(config):
    """Determine which account to use.

    In order to make the renewer (configuration de/serialization) happy,
    if ``config.account`` is ``None``, it will be updated based on the
    user input. Same for ``config.email``.

    :param config: Configuration object
    :type config: interfaces.IConfig

    :returns: Account and optionally ACME client API (biproduct of new
        registration).
    :rtype: tuple of :class:`certbot.account.Account` and :class:`acme.client.Client`

    :raises errors.Error: If unable to register an account with ACME server

    """
    account_storage = account.AccountFileStorage(config)
    acme = None

    if config.account is not None:
        acc = account_storage.load(config.account)
    else:
        accounts = account_storage.find_all()
        if len(accounts) > 1:
            acc = display_ops.choose_account(accounts)
        elif len(accounts) == 1:
            acc = accounts[0]
        else:  # no account registered yet
            if config.email is None and not config.register_unsafely_without_email:
                config.email = display_ops.get_email()

            def _tos_cb(regr):
                if config.tos:
                    return True
                msg = ("Please read the Terms of Service at {0}. You "
                       "must agree in order to register with the ACME "
                       "server at {1}".format(
                           regr.terms_of_service, config.server))
                obj = zope.component.getUtility(interfaces.IDisplay)
                return obj.yesno(msg, "Agree", "Cancel",
                                 cli_flag="--agree-tos", force_interactive=True)

            try:
                acc, acme = client.register(
                    config, account_storage, tos_cb=_tos_cb)
            except errors.MissingCommandlineFlag:
                raise
            except errors.Error as error:
                logger.debug(error, exc_info=True)
                raise errors.Error(
                    "Unable to register an account with ACME server")

    config.account = acc.id
    return acc, acme


def _delete_if_appropriate(config): # pylint: disable=too-many-locals,too-many-branches
    """Does the user want to delete their now-revoked certs? If run in non-interactive mode,
    deleting happens automatically, unless if both `--cert-name` and `--cert-path` were
    specified with conflicting values.

    :param config: parsed command line arguments
    :type config: interfaces.IConfig

    :returns: `None`
    :rtype: None

    :raises errors.Error: If anything goes wrong, including bad user input, if an overlapping
        archive dir is found for the specified lineage, etc ...
    """
    display = zope.component.getUtility(interfaces.IDisplay)
    reporter_util = zope.component.getUtility(interfaces.IReporter)

    attempt_deletion = config.delete_after_revoke
    if attempt_deletion is None:
        msg = ("Would you like to delete the cert(s) you just revoked?")
        attempt_deletion = display.yesno(msg, yes_label="Yes (recommended)", no_label="No",
                force_interactive=True, default=True)

    if not attempt_deletion:
        reporter_util.add_message("Not deleting revoked certs.", reporter_util.LOW_PRIORITY)
        return

    if not (config.certname or config.cert_path):
        raise errors.Error('At least one of --cert-path or --cert-name must be specified.')

    if config.certname and config.cert_path:
        # first, check if certname and cert_path imply the same certs
        implied_cert_name = cert_manager.cert_path_to_lineage(config)

        if implied_cert_name != config.certname:
            cert_path_implied_cert_name = cert_manager.cert_path_to_lineage(config)
            cert_path_implied_conf = storage.renewal_file_for_certname(config,
                    cert_path_implied_cert_name)
            cert_path_cert = storage.RenewableCert(cert_path_implied_conf, config)
            cert_path_info = cert_manager.human_readable_cert_info(config, cert_path_cert,
                    skip_filter_checks=True)

            cert_name_implied_conf = storage.renewal_file_for_certname(config, config.certname)
            cert_name_cert = storage.RenewableCert(cert_name_implied_conf, config)
            cert_name_info = cert_manager.human_readable_cert_info(config, cert_name_cert)

            msg = ("You specified conflicting values for --cert-path and --cert-name. "
                    "Which did you mean to select?")
            choices = [cert_path_info, cert_name_info]
            try:
                code, index = display.menu(msg,
                        choices, ok_label="Select", force_interactive=True)
            except errors.MissingCommandlineFlag:
                error_msg = ('To run in non-interactive mode, you must either specify only one of '
                '--cert-path or --cert-name, or both must point to the same certificate lineages.')
                raise errors.Error(error_msg)

            if code != display_util.OK or not index in range(0, len(choices)):
                raise errors.Error("User ended interaction.")

            if index == 0:
                config.certname = cert_path_implied_cert_name
            else:
                config.cert_path = storage.cert_path_for_cert_name(config, config.certname)

    elif config.cert_path:
        config.certname = cert_manager.cert_path_to_lineage(config)

    else: # if only config.certname was specified
        config.cert_path = storage.cert_path_for_cert_name(config, config.certname)

    # don't delete if the archive_dir is used by some other lineage
    archive_dir = storage.full_archive_path(
            configobj.ConfigObj(storage.renewal_file_for_certname(config, config.certname)),
            config, config.certname)
    try:
        cert_manager.match_and_check_overlaps(config, [lambda x: archive_dir],
            lambda x: x.archive_dir, lambda x: x)
    except errors.OverlappingMatchFound:
        msg = ('Not deleting revoked certs due to overlapping archive dirs. More than '
                'one lineage is using {0}'.format(archive_dir))
        reporter_util.add_message(''.join(msg), reporter_util.MEDIUM_PRIORITY)
        return
    except Exception as e:
        msg = ('config.default_archive_dir: {0}, config.live_dir: {1}, archive_dir: {2},'
        'original exception: {3}')
        msg = msg.format(config.default_archive_dir, config.live_dir, archive_dir, e)
        raise errors.Error(msg)

    cert_manager.delete(config)


def _init_le_client(config, authenticator, installer):
    """Initialize Let's Encrypt Client

    :param config: Configuration object
    :type config: interfaces.IConfig

    :param authenticator: Acme authentication handler
    :type authenticator: interfaces.IAuthenticator
    :param installer: Installer object
    :type installer: interfaces.IInstaller

    :returns: client: Client object
    :rtype: client.Client

    """
    if authenticator is not None:
        # if authenticator was given, then we will need account...
        acc, acme = _determine_account(config)
        logger.debug("Picked account: %r", acc)
        # XXX
        #crypto_util.validate_key_csr(acc.key)
    else:
        acc, acme = None, None

    return client.Client(config, acc, authenticator, installer, acme=acme)


def unregister(config, unused_plugins):
    """Deactivate account on server

    :param config: Configuration object
    :type config: interfaces.IConfig

    :param unused_plugins: List of plugins (deprecated)
    :type unused_plugins: `list` of `str`

    :returns: `None`
    :rtype: None

    """
    account_storage = account.AccountFileStorage(config)
    accounts = account_storage.find_all()
    reporter_util = zope.component.getUtility(interfaces.IReporter)

    if not accounts:
        return "Could not find existing account to deactivate."
    yesno = zope.component.getUtility(interfaces.IDisplay).yesno
    prompt = ("Are you sure you would like to irrevocably deactivate "
              "your account?")
    wants_deactivate = yesno(prompt, yes_label='Deactivate', no_label='Abort',
                             default=True)

    if not wants_deactivate:
        return "Deactivation aborted."

    acc, acme = _determine_account(config)
    cb_client = client.Client(config, acc, None, None, acme=acme)

    # delete on boulder
    cb_client.acme.deactivate_registration(acc.regr)
    account_files = account.AccountFileStorage(config)
    # delete local account files
    account_files.delete(config.account)

    reporter_util.add_message("Account deactivated.", reporter_util.MEDIUM_PRIORITY)


def register(config, unused_plugins):
    """Create or modify accounts on the server.

    :param config: Configuration object
    :type config: interfaces.IConfig

    :param unused_plugins: List of plugins (deprecated)
    :type unused_plugins: `list` of `str`

    :returns: `None` or a string indicating and error
    :rtype: None or str

    """
    # Portion of _determine_account logic to see whether accounts already
    # exist or not.
    account_storage = account.AccountFileStorage(config)
    accounts = account_storage.find_all()
    reporter_util = zope.component.getUtility(interfaces.IReporter)
    add_msg = lambda m: reporter_util.add_message(m, reporter_util.MEDIUM_PRIORITY)

    # registering a new account
    if not config.update_registration:
        if len(accounts) > 0:
            # TODO: add a flag to register a duplicate account (this will
            #       also require extending _determine_account's behavior
            #       or else extracting the registration code from there)
            return ("There is an existing account; registration of a "
                    "duplicate account with this command is currently "
                    "unsupported.")
        # _determine_account will register an account
        _determine_account(config)
        return

    # --update-registration
    if len(accounts) == 0:
        return "Could not find an existing account to update."
    if config.email is None:
        if config.register_unsafely_without_email:
            return ("--register-unsafely-without-email provided, however, a "
                    "new e-mail address must\ncurrently be provided when "
                    "updating a registration.")
        config.email = display_ops.get_email(optional=False)

    acc, acme = _determine_account(config)
    cb_client = client.Client(config, acc, None, None, acme=acme)
    # We rely on an exception to interrupt this process if it didn't work.
    acc.regr = cb_client.acme.update_registration(acc.regr.update(
        body=acc.regr.body.update(contact=('mailto:' + config.email,))))
    account_storage.save_regr(acc, cb_client.acme)
    eff.handle_subscription(config)
    add_msg("Your e-mail address was updated to {0}.".format(config.email))

def _install_cert(config, le_client, domains, lineage=None):
    """Install a cert

    :param config: Configuration object
    :type config: interfaces.IConfig

    :param le_client: Client object
    :type le_client: client.Client

    :param plugins: List of domains
    :type plugins: `list` of `str`

    :param lineage: Certificate lineage object. Defaults to `None`
    :type lineage: storage.RenewableCert

    :returns: `None`
    :rtype: None

    """
    path_provider = lineage if lineage else config
    assert path_provider.cert_path is not None

    le_client.deploy_certificate(domains, path_provider.key_path,
        path_provider.cert_path, path_provider.chain_path, path_provider.fullchain_path)
    le_client.enhance_config(domains, path_provider.chain_path)

def install(config, plugins):
    """Install a previously obtained cert in a server.

    :param config: Configuration object
    :type config: interfaces.IConfig

    :param plugins: List of plugins
    :type plugins: `list` of `str`

    :returns: `None`
    :rtype: None

    """
    # XXX: Update for renewer/RenewableCert
    # FIXME: be consistent about whether errors are raised or returned from
    # this function ...

    try:
        installer, _ = plug_sel.choose_configurator_plugins(config, plugins, "install")
    except errors.PluginSelectionError as e:
        return str(e)

    domains, _ = _find_domains_or_certname(config, installer)
    le_client = _init_le_client(config, authenticator=None, installer=installer)
    _install_cert(config, le_client, domains)


def plugins_cmd(config, plugins):
    """List server software plugins.

    :param config: Configuration object
    :type config: interfaces.IConfig

    :param plugins: List of plugins
    :type plugins: `list` of `str`

    :returns: `None`
    :rtype: None

    """
    logger.debug("Expected interfaces: %s", config.ifaces)

    ifaces = [] if config.ifaces is None else config.ifaces
    filtered = plugins.visible().ifaces(ifaces)
    logger.debug("Filtered plugins: %r", filtered)

    notify = functools.partial(zope.component.getUtility(
        interfaces.IDisplay).notification, pause=False)
    if not config.init and not config.prepare:
        notify(str(filtered))
        return

    filtered.init(config)
    verified = filtered.verify(ifaces)
    logger.debug("Verified plugins: %r", verified)

    if not config.prepare:
        notify(str(verified))
        return

    verified.prepare()
    available = verified.available()
    logger.debug("Prepared plugins: %s", available)
    notify(str(available))


def rollback(config, plugins):
    """Rollback server configuration changes made during install.

    :param config: Configuration object
    :type config: interfaces.IConfig

    :param plugins: List of plugins
    :type plugins: `list` of `str`

    :returns: `None`
    :rtype: None

    """
    client.rollback(config.installer, config.checkpoints, config, plugins)


def config_changes(config, unused_plugins):
    """Show changes made to server config during installation

    View checkpoints and associated configuration changes.

    :param config: Configuration object
    :type config: interfaces.IConfig

    :param unused_plugins: List of plugins (deprecated)
    :type unused_plugins: `list` of `str`

    :returns: `None`
    :rtype: None

    """
    client.view_config_changes(config, num=config.num)

def update_symlinks(config, unused_plugins):
    """Update the certificate file family symlinks

    Use the information in the config file to make symlinks point to
    the correct archive directory.

    :param config: Configuration object
    :type config: interfaces.IConfig

    :param unused_plugins: List of plugins (deprecated)
    :type unused_plugins: `list` of `str`

    :returns: `None`
    :rtype: None

    """
    cert_manager.update_live_symlinks(config)

def rename(config, unused_plugins):
    """Rename a certificate

    Use the information in the config file to rename an existing
    lineage.

    :param config: Configuration object
    :type config: interfaces.IConfig

    :param unused_plugins: List of plugins (deprecated)
    :type unused_plugins: `list` of `str`

    :returns: `None`
    :rtype: None

    """
    cert_manager.rename_lineage(config)

def delete(config, unused_plugins):
    """Delete a certificate

    Use the information in the config file to delete an existing
    lineage.

    :param config: Configuration object
    :type config: interfaces.IConfig

    :param unused_plugins: List of plugins (deprecated)
    :type unused_plugins: `list` of `str`

    :returns: `None`
    :rtype: None

    """
    cert_manager.delete(config)

def certificates(config, unused_plugins):
    """Display information about certs configured with Certbot

    :param config: Configuration object
    :type config: interfaces.IConfig

    :param unused_plugins: List of plugins (deprecated)
    :type unused_plugins: `list` of `str`

    :returns: `None`
    :rtype: None

    """
    cert_manager.certificates(config)

def revoke(config, unused_plugins):  # TODO: coop with renewal config
    """Revoke a previously obtained certificate.

    :param config: Configuration object
    :type config: interfaces.IConfig

    :param unused_plugins: List of plugins (deprecated)
    :type unused_plugins: `list` of `str`

    :returns: `None` or string indicating error in case of error
    :rtype: None or str

    """
    # For user-agent construction
    config.installer = config.authenticator = "None"
    if config.key_path is not None:  # revocation by cert key
        logger.debug("Revoking %s using cert key %s",
                     config.cert_path[0], config.key_path[0])
        crypto_util.verify_cert_matches_priv_key(config.cert_path[0], config.key_path[0])
        key = jose.JWK.load(config.key_path[1])
    else:  # revocation by account key
        logger.debug("Revoking %s using Account Key", config.cert_path[0])
        acc, _ = _determine_account(config)
        key = acc.key
    acme = client.acme_from_config_key(config, key)
    cert = crypto_util.pyopenssl_load_certificate(config.cert_path[1])[0]
    logger.debug("Reason code for revocation: %s", config.reason)

    try:
        acme.revoke(jose.ComparableX509(cert), config.reason)
        _delete_if_appropriate(config)
    except acme_errors.ClientError as e:
        return str(e)

    display_ops.success_revocation(config.cert_path[0])


def run(config, plugins):  # pylint: disable=too-many-branches,too-many-locals
    """Obtain a certificate and install.

    :param config: Configuration object
    :type config: interfaces.IConfig

    :param plugins: List of plugins
    :type plugins: `list` of `str`

    :returns: `None`
    :rtype: None

    """
    # TODO: Make run as close to auth + install as possible
    # Possible difficulties: config.csr was hacked into auth
    try:
        installer, authenticator = plug_sel.choose_configurator_plugins(config, plugins, "run")
    except errors.PluginSelectionError as e:
        return str(e)

    # TODO: Handle errors from _init_le_client?
    le_client = _init_le_client(config, authenticator, installer)

    domains, certname = _find_domains_or_certname(config, installer)
    should_get_cert, lineage = _find_cert(config, domains, certname)

    new_lineage = lineage
    if should_get_cert:
        new_lineage = _get_and_save_cert(le_client, config, domains,
            certname, lineage)

    cert_path = new_lineage.cert_path if new_lineage else None
    fullchain_path = new_lineage.fullchain_path if new_lineage else None
    key_path = new_lineage.key_path if new_lineage else None
    _report_new_cert(config, cert_path, fullchain_path, key_path)

    _install_cert(config, le_client, domains, new_lineage)

    if lineage is None or not should_get_cert:
        display_ops.success_installation(domains)
    else:
        display_ops.success_renewal(domains)

    _suggest_donation_if_appropriate(config)


def _csr_get_and_save_cert(config, le_client):
    """Obtain a cert using a user-supplied CSR

    This works differently in the CSR case (for now) because we don't
    have the privkey, and therefore can't construct the files for a lineage.
    So we just save the cert & chain to disk :/

    :param config: Configuration object
    :type config: interfaces.IConfig

    :param client: Client object
    :type client: client.Client

    :returns: `cert_path` and `fullchain_path` as absolute paths to the actual files
    :rtype: `tuple` of `str`

    """
    csr, _ = config.actual_csr
    certr, chain = le_client.obtain_certificate_from_csr(config.domains, csr)
    if config.dry_run:
        logger.debug(
            "Dry run: skipping saving certificate to %s", config.cert_path)
        return None, None
    cert_path, _, fullchain_path = le_client.save_certificate(
            certr, chain, config.cert_path, config.chain_path, config.fullchain_path)
    return cert_path, fullchain_path

def renew_cert(config, plugins, lineage):
    """Renew & save an existing cert. Do not install it.

    :param config: Configuration object
    :type config: interfaces.IConfig

    :param plugins: List of plugins
    :type plugins: `list` of `str`

    :param lineage: Certificate lineage object
    :type lineage: storage.RenewableCert

    :returns: `None`
    :rtype: None

    :raises errors.PluginSelectionError: MissingCommandlineFlag if supplied parameters do not pass

    """
    try:
        # installers are used in auth mode to determine domain names
        installer, auth = plug_sel.choose_configurator_plugins(config, plugins, "certonly")
    except errors.PluginSelectionError as e:
        logger.info("Could not choose appropriate plugin: %s", e)
        raise

    le_client = _init_le_client(config, auth, installer)

    _get_and_save_cert(le_client, config, lineage=lineage)

    notify = zope.component.getUtility(interfaces.IDisplay).notification
    if installer is None:
        notify("new certificate deployed without reload, fullchain is {0}".format(
               lineage.fullchain), pause=False)
    else:
        # In case of a renewal, reload server to pick up new certificate.
        # In principle we could have a configuration option to inhibit this
        # from happening.
        installer.restart()
        notify("new certificate deployed with reload of {0} server; fullchain is {1}".format(
               config.installer, lineage.fullchain), pause=False)

def certonly(config, plugins):
    """Authenticate & obtain cert, but do not install it.

    This implements the 'certonly' subcommand.

    :param config: Configuration object
    :type config: interfaces.IConfig

    :param plugins: List of plugins
    :type plugins: `list` of `str`

    :returns: `None`
    :rtype: None

    :raises errors.Error: If specified plugin could not be used

    """
    # SETUP: Select plugins and construct a client instance
    try:
        # installers are used in auth mode to determine domain names
        installer, auth = plug_sel.choose_configurator_plugins(config, plugins, "certonly")
    except errors.PluginSelectionError as e:
        logger.info("Could not choose appropriate plugin: %s", e)
        raise

    le_client = _init_le_client(config, auth, installer)

    if config.csr:
        cert_path, fullchain_path = _csr_get_and_save_cert(config, le_client)
        _report_new_cert(config, cert_path, fullchain_path)
        _suggest_donation_if_appropriate(config)
        return

    domains, certname = _find_domains_or_certname(config, installer)
    should_get_cert, lineage = _find_cert(config, domains, certname)

    if not should_get_cert:
        notify = zope.component.getUtility(interfaces.IDisplay).notification
        notify("Certificate not yet due for renewal; no action taken.", pause=False)
        return

    lineage = _get_and_save_cert(le_client, config, domains, certname, lineage)

    cert_path = lineage.cert_path if lineage else None
    fullchain_path = lineage.fullchain_path if lineage else None
    key_path = lineage.key_path if lineage else None
    _report_new_cert(config, cert_path, fullchain_path, key_path)
    _suggest_donation_if_appropriate(config)

def renew(config, unused_plugins):
    """Renew previously-obtained certificates.

    :param config: Configuration object
    :type config: interfaces.IConfig

    :param unused_plugins: List of plugins (deprecated)
    :type unused_plugins: `list` of `str`

    :returns: `None`
    :rtype: None

    """
    try:
        renewal.handle_renewal_request(config)
    finally:
        hooks.run_saved_post_hooks()


def make_or_verify_needed_dirs(config):
    """Create or verify existence of config, work, and hook directories.

    :param config: Configuration object
    :type config: interfaces.IConfig

    :returns: `None`
    :rtype: None

    """
    util.set_up_core_dir(config.config_dir, constants.CONFIG_DIRS_MODE,
                         os.geteuid(), config.strict_permissions)
    util.set_up_core_dir(config.work_dir, constants.CONFIG_DIRS_MODE,
                         os.geteuid(), config.strict_permissions)

    hook_dirs = (config.renewal_pre_hooks_dir,
                 config.renewal_deploy_hooks_dir,
                 config.renewal_post_hooks_dir,)
    for hook_dir in hook_dirs:
        util.make_or_verify_dir(hook_dir,
                                uid=os.geteuid(),
                                strict=config.strict_permissions)


def set_displayer(config):
    """Set the displayer

    :param config: Configuration object
    :type config: interfaces.IConfig

    :returns: `None`
    :rtype: None

    """
    if config.quiet:
        config.noninteractive_mode = True
        displayer = display_util.NoninteractiveDisplay(open(os.devnull, "w"))
    elif config.noninteractive_mode:
        displayer = display_util.NoninteractiveDisplay(sys.stdout)
    else:
        displayer = display_util.FileDisplay(sys.stdout,
                                             config.force_interactive)
    zope.component.provideUtility(displayer)


def main(cli_args=sys.argv[1:]):
    """Command line argument parsing and main script execution.

    :returns: result of requested command

    :raises errors.Error: OS errors triggered by wrong permissions
    :raises errors.Error: error if plugin command is not supported

    """
    log.pre_arg_parse_setup()

    plugins = plugins_disco.PluginsRegistry.find_all()
    logger.debug("certbot version: %s", certbot.__version__)
    # do not log `config`, as it contains sensitive data (e.g. revoke --key)!
    logger.debug("Arguments: %r", cli_args)
    logger.debug("Discovered plugins: %r", plugins)

    # note: arg parser internally handles --help (and exits afterwards)
    args = cli.prepare_and_parse_args(plugins, cli_args)
    config = configuration.NamespaceConfig(args)
    zope.component.provideUtility(config)

    try:
        log.post_arg_parse_setup(config)
        make_or_verify_needed_dirs(config)
    except errors.Error:
        # Let plugins_cmd be run as un-privileged user.
        if config.func != plugins_cmd:
            raise
    deprecation_fmt = (
        "Python %s.%s support will be dropped in the next "
        "release of Certbot - please upgrade your Python version.")
    # We use the warnings system for Python 2.6 and logging for Python 3
    # because DeprecationWarnings are only reported by default in Python <= 2.6
    # and warnings can be disabled by the user.
    if sys.version_info[:2] == (2, 6):
        warning = deprecation_fmt % sys.version_info[:2]
        warnings.warn(warning, DeprecationWarning)
    elif sys.version_info[:2] == (3, 3):
        logger.warning(deprecation_fmt, *sys.version_info[:2])

    set_displayer(config)

    # Reporter
    report = reporter.Reporter(config)
    zope.component.provideUtility(report)
    util.atexit_register(report.print_messages)

    return config.func(config, plugins)


if __name__ == "__main__":
    err_string = main()
    if err_string:
        logger.warning("Exiting with message %s", err_string)
    sys.exit(err_string)  # pragma: no cover
