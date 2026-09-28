from ansible_base.resource_registry.fields import AnsibleResourceField
from django.db import models


class Credential(models.Model):
    """
    Minimal, PoC-scoped canonical copy of a secret-free Credential instance
    (e.g. a "HashiCorp Vault Secret Lookup (OIDC)" credential). Gateway is the
    authoritative owner for this resource type - see credential-resource-sync-poc
    plan. Only credential types that pass `is_secret_free_credential_type()` are
    ever reverse-synced into this table by Controller/EDA (see their pre_save
    eligibility gates); this model intentionally has no encrypted-field support,
    since it must never hold secret material.

    NOTE: `name` is globally unique here as a PoC simplification. Production
    Controller allows the same name across different organizations/types
    (unique_together on organization+name+credential_type); this PoC narrows
    that so `GetOrCreateProcessor`'s get-or-create-by-unique-field lookup can
    reconcile independent pushes from Controller and EDA without collision.
    """

    class Meta:
        app_label = 'aap_gateway_api'

    resource = AnsibleResourceField(primary_key_field="id")

    name = models.CharField(max_length=512, unique=True)
    organization = models.ForeignKey(
        'aap_gateway_api.Organization',
        related_name='credentials',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    # Name of a CredentialType that's expected to already exist, identically
    # named, on every consuming service (e.g. "HashiCorp Vault Secret Lookup
    # (OIDC)") - not a synced resource itself, see SharedCredential.
    credential_type_name = models.CharField(max_length=512)
    inputs = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name
