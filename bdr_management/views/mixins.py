from django.core.exceptions import ObjectDoesNotExist

from bdr_registry.models import Account, Company, Obligation


class CompanyMixin(object):
    def get_obligations(self, default=True, no_user=False):
        if not no_user:
            obligations = self.request.user and self.request.user.obligations.values()
        else:
            obligations = False
            default = True
        if default and not obligations:
            obligations = Obligation.objects.values()
        return [o["id"] for o in obligations]

    def get_companies(self, default=True, no_user=False):
        o_ids = self.get_obligations(default=default, no_user=no_user)
        return Company.objects.filter(obligation__id__in=o_ids).all()

    def get_account(self, uid):
        try:
            return Account.objects.get(uid=uid)
        except ObjectDoesNotExist:
            return None

    def get_account_company(self, uid):
        account = self.get_account(uid)
        if account:
            try:
                return Company.objects.get(account=account)
            except ObjectDoesNotExist:
                return None

    def dispatch(self, request, *args, **kwargs):
        # if request.user and not request.user.obligations.count():
        #     messages.warning(
        #         request, _('You have no obligations assigned to this user')
        #     )
        return super(CompanyMixin, self).dispatch(request, *args, **kwargs)
