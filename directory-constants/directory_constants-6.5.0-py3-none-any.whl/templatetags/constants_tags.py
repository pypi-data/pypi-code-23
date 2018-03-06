from directory_constants.constants import urls

from django import template

register = template.Library()

url_map = {
    "great_home": urls.GREAT_HOME,
    "exporting_is_great": urls.GREAT_EXPORT_HOME,
    "new_to_exporting": urls.EXPORTING_NEW,
    "occasional_exporter": urls.EXPORTING_OCCASIONAL,
    "regular_exporter": urls.EXPORTING_REGULAR,
    "market_research": urls.GUIDANCE_MARKET_RESEARCH,
    "customer_insight": urls.GUIDANCE_CUSTOMER_INSIGHT,
    "finance": urls.GUIDANCE_FINANCE,
    "business_planning": urls.GUIDANCE_BUSINESS_PLANNING,
    "getting_paid": urls.GUIDANCE_GETTING_PAID,
    "operations_and_compliance": urls.GUIDANCE_OPERATIONS_AND_COMPLIANCE,
    "events": urls.SERVICES_EVENTS,
    "export_opportunities": urls.SERVICES_EXOPPS,
    "find_a_buyer": urls.SERVICES_FAB,
    "get_finance": urls.SERVICES_GET_FINANCE,
    "selling_online_overseas": urls.SERVICES_SOO,
    "contact_directory": urls.INFO_CONTACT_US_DIRECTORY,
    "contact_sso": urls.INFO_CONTACT_US_SSO,
    "terms": urls.INFO_TERMS_AND_CONDITIONS,
    "about": urls.INFO_ABOUT,
    "privacy": urls.INFO_PRIVACY_AND_COOKIES,
    "DIT": urls.INFO_DIT,
    "feedback_directory": urls.FEEDBACK_FORM_DIRECTORY,
    "feedback_sso": urls.FEEDBACK_FORM_SSO,
}


@register.simple_tag
def external_url(name):
    assert name in url_map, 'URL name "{name}"" not found'.format(name=name)
    return url_map[name]
