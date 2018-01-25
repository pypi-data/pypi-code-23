"""Models related to domains management."""

from __future__ import unicode_literals

import datetime

from django.db import models
from django.utils import timezone
from django.utils.encoding import (
    python_2_unicode_compatible, smart_text, force_text
)
from django.utils.functional import cached_property
from django.utils.translation import ugettext as _, ugettext_lazy

from reversion import revisions as reversion

from modoboa.core import signals as core_signals
from modoboa.core.models import User
from modoboa.lib.exceptions import BadRequest, Conflict
from modoboa.parameters import tools as param_tools

from .base import AdminObject
from .. import constants


@python_2_unicode_compatible
class Domain(AdminObject):
    """Mail domain."""

    name = models.CharField(ugettext_lazy('name'), max_length=100, unique=True,
                            help_text=ugettext_lazy("The domain name"))
    quota = models.PositiveIntegerField(
        default=0,
        help_text=ugettext_lazy(
            "Quota in MB shared between mailboxes. A value of 0 means "
            "no quota."
        )
    )
    default_mailbox_quota = models.PositiveIntegerField(
        verbose_name=ugettext_lazy("Default mailbox quota"),
        default=0,
        help_text=ugettext_lazy(
            "Default quota in MB applied to mailboxes. A value of 0 means "
            "no quota."
        )
    )
    enabled = models.BooleanField(
        ugettext_lazy('enabled'),
        help_text=ugettext_lazy("Check to activate this domain"),
        default=True
    )
    type = models.CharField(default="domain", max_length=20)
    enable_dns_checks = models.BooleanField(
        ugettext_lazy("Enable DNS checks"), default=True,
        help_text=ugettext_lazy("Check to enable DNS checks for this domain")
    )

    transport = models.OneToOneField(
        "transport.Transport", null=True, on_delete=models.SET_NULL)

    enable_dkim = models.BooleanField(
        ugettext_lazy("Enable DKIM signing"),
        help_text=ugettext_lazy(
            "If you activate this feature, a DKIM key will be "
            "generated for this domain."),
        default=False
    )
    dkim_key_selector = models.CharField(max_length=30, default="modoboa")
    dkim_key_length = models.PositiveIntegerField(
        ugettext_lazy("Key length"), choices=constants.DKIM_KEY_LENGTHS,
        blank=True, null=True
    )
    dkim_public_key = models.TextField(blank=True)
    dkim_private_key_path = models.CharField(max_length=254, blank=True)

    class Meta:
        permissions = (
            ("view_domain", "View domain"),
            ("view_domains", "View domains"),
        )
        ordering = ["name"]
        app_label = "admin"

    def __init__(self, *args, **kwargs):
        """Save name for further use."""
        super(Domain, self).__init__(*args, **kwargs)
        self.old_mail_homes = None
        self.oldname = self.name

    @property
    def domainalias_count(self):
        return self.domainalias_set.count()

    @property
    def mailbox_count(self):
        return self.mailbox_set.count()

    @property
    def mbalias_count(self):
        return self.alias_set.filter(internal=False).count()

    @property
    def identities_count(self):
        """Total number of identities in this domain."""
        return (
            self.mailbox_set.count() +
            self.alias_set.filter(internal=False).count())

    @property
    def tags(self):
        label = ""
        for dt in constants.DOMAIN_TYPES:
            if self.type == dt[0]:
                label = dt[1]
        result = [{"name": self.type, "label": label, "type": "dom"}]
        if self.transport:
            result.append({
                "name": self.transport.service,
                "label": self.transport.service,
                "type": "srv",
                "color": "info"
            })
        return result

    @property
    def admins(self):
        """Return the domain administrators of this domain.

        :return: a list of User objects
        """
        return User.objects.filter(
            is_superuser=False,
            objectaccess__content_type__model="domain",
            objectaccess__object_id=self.pk)

    @property
    def aliases(self):
        return self.domainalias_set

    @property
    def uses_a_reserved_tld(self):
        """Does this domain use a reserved TLD."""
        tld = self.name.split(".", 1)[-1]
        return tld in constants.RESERVED_TLD

    @property
    def just_created(self):
        """Return true if the domain was created in the latest 24h."""
        now = timezone.now()
        delta = datetime.timedelta(days=1)
        return self.creation + delta > now

    def awaiting_checks(self):
        """Return true if the domain has no valid MX record and was created
        in the latest 24h."""
        if (not self.mxrecord_set.has_valids()) and self.just_created:
            return True
        return False

    @cached_property
    def dnsbl_status_color(self):
        """Shortcut to DNSBL results."""
        if not self.dnsblresult_set.exists():
            return "warning"
        elif self.dnsblresult_set.blacklisted().exists():
            return "danger"
        else:
            return "success"

    @cached_property
    def allocated_quota(self):
        """Return current quota allocation."""
        if not self.quota:
            return 0
        if not self.mailbox_set.exists():
            return 0
        return self.mailbox_set.aggregate(
            total=models.Sum("quota"))["total"]

    @cached_property
    def allocated_quota_in_percent(self):
        """Return allocated quota in percent."""
        if not self.allocated_quota:
            return 0
        return int(self.allocated_quota / float(self.quota) * 100)

    @cached_property
    def used_quota(self):
        """Return current quota usage."""
        from .mailbox import Quota

        if not self.quota:
            return 0
        if not self.mailbox_set.exists():
            return 0
        return int(Quota.objects.get_domain_usage(self) / 1048576)

    @cached_property
    def used_quota_in_percent(self):
        """Return used quota in percent."""
        if not self.allocated_quota:
            return 0
        return int(self.used_quota / float(self.quota) * 100)

    @property
    def bind_format_dkim_public_key(self):
        """Return DKIM public key using Bind format."""
        return "{}._domainkey 10800 IN TXT \"v=DKIM1; k=rsa; p={}\"".format(
            self.dkim_key_selector, self.dkim_public_key)

    def add_admin(self, account):
        """Add a new administrator to this domain.

        :param User account: the administrator
        """
        from modoboa.lib.permissions import grant_access_to_object

        core_signals.can_create_object.send(
            sender=self.__class__, context=self, object_type="domain_admins")
        grant_access_to_object(account, self)
        for mb in self.mailbox_set.all():
            if mb.user.has_perm("admin.add_domain"):
                continue
            grant_access_to_object(account, mb)
            grant_access_to_object(account, mb.user)
        for al in self.alias_set.all():
            grant_access_to_object(account, al)

    def remove_admin(self, account):
        """Remove an administrator of this domain.

        :param User account: administrator to remove
        """
        from modoboa.lib.permissions import ungrant_access_to_object

        ungrant_access_to_object(self, account)
        for mb in self.mailbox_set.all():
            if mb.user.has_perm("admin.add_domain"):
                continue
            ungrant_access_to_object(mb, account)
            ungrant_access_to_object(mb.user, account)
        for al in self.alias_set.all():
            ungrant_access_to_object(al, account)

    def save(self, *args, **kwargs):
        """Store current data if domain is renamed."""
        if self.oldname != self.name:
            self.old_mail_homes = (
                dict((mb.id, mb.mail_home) for mb in self.mailbox_set.all())
            )
        super(Domain, self).save(*args, **kwargs)

    def delete(self, fromuser, keepdir=False):
        """Custom delete method."""
        from modoboa.lib.permissions import ungrant_access_to_objects
        from .mailbox import Quota

        if self.domainalias_set.count():
            ungrant_access_to_objects(self.domainalias_set.all())
        if self.alias_set.count():
            ungrant_access_to_objects(self.alias_set.all())
        if param_tools.get_global_parameter("auto_account_removal"):
            User.objects.filter(mailbox__domain=self).delete()
        elif self.mailbox_set.count():
            Quota.objects.filter(username__contains="@%s" % self.name).delete()
            ungrant_access_to_objects(self.mailbox_set.all())
        super(Domain, self).delete()

    def __str__(self):
        return smart_text(self.name)

    def from_csv(self, user, row):
        """Create a new domain from a CSV entry.

        The expected fields order is the following::

          "domain", name, quota, default_mailbox_quota, enabled

        :param ``core.User`` user: user creating the domain
        :param str row: a list containing domain's definition
        """
        from .. import lib

        if len(row) < 5:
            raise BadRequest(_("Invalid line"))
        self.name = row[1].strip()
        if Domain.objects.filter(name=self.name).exists():
            raise Conflict
        domains_must_have_authorized_mx = (
            param_tools.get_global_parameter("domains_must_have_authorized_mx")
        )
        if domains_must_have_authorized_mx and not user.is_superuser:
            if not lib.domain_has_authorized_mx(self.name):
                raise BadRequest(
                    _("No authorized MX record found for domain {}")
                    .format(self.name)
                )
        try:
            self.quota = int(row[2].strip())
        except ValueError:
            raise BadRequest(
                _("Invalid quota value for domain '{}'")
                .format(self.name)
            )
        try:
            self.default_mailbox_quota = int(row[3].strip())
        except ValueError:
            raise BadRequest(
                _("Invalid default mailbox quota value for domain '{}'")
                .format(self.name)
            )
        if self.quota != 0 and self.default_mailbox_quota > self.quota:
            raise BadRequest(
                _("Default mailbox quota cannot be greater than domain "
                  "quota")
            )
        self.enabled = (row[4].strip().lower() in ["true", "1", "yes", "y"])
        core_signals.can_create_object.send(
            sender=self.__class__, context=user, klass=Domain,
            instance=self)
        self.save(creator=user)

    def to_csv(self, csvwriter):
        """Export domain and domain aliases to CSV format."""
        csvwriter.writerow([
            "domain",
            force_text(self.name),
            self.quota,
            self.default_mailbox_quota,
            self.enabled
        ])
        for dalias in self.domainalias_set.all():
            dalias.to_csv(csvwriter)

    def post_create(self, creator):
        """Post creation actions.

        :param ``User`` creator: user whos created this domain
        """
        super(Domain, self).post_create(creator)
        for domalias in self.domainalias_set.all():
            domalias.post_create(creator)


reversion.register(Domain)
