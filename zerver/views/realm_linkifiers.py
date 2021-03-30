from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.utils.translation import ugettext as _

from zerver.decorator import require_realm_admin
from zerver.lib.actions import do_add_linkifier, do_remove_linkifier
from zerver.lib.request import REQ, has_request_variables
from zerver.lib.response import json_error, json_success
from zerver.models import RealmFilter, UserProfile, linkifiers_for_realm


# Custom realm linkifiers
def list_linkifiers(request: HttpRequest, user_profile: UserProfile) -> HttpResponse:
    filters = linkifiers_for_realm(user_profile.realm_id)
    return json_success({"filters": filters})


@require_realm_admin
@has_request_variables
def create_linkifier(
    request: HttpRequest,
    user_profile: UserProfile,
    pattern: str = REQ(),
    url_format_string: str = REQ(),
) -> HttpResponse:
    try:
        linkifier_id = do_add_linkifier(
            realm=user_profile.realm,
            pattern=pattern,
            url_format_string=url_format_string,
        )
        return json_success({"id": linkifier_id})
    except ValidationError as e:
        return json_error(e.messages[0], data={"errors": dict(e)})


@require_realm_admin
def delete_linkifier(
    request: HttpRequest, user_profile: UserProfile, filter_id: int
) -> HttpResponse:
    try:
        do_remove_linkifier(realm=user_profile.realm, id=filter_id)
    except RealmFilter.DoesNotExist:
        return json_error(_("Filter not found"))
    return json_success()
