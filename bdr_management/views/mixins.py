from bdr_registry.models import Obligation, Company


class CompanyMixin(object):
    def get_obligations(self, default=True):
        obligations = (
            self.request.user and self.request.user.obligations.values()
        )
        if default and not obligations:
            obligations = Obligation.objects.values()
        return [o['id'] for o in obligations]

    def get_companies(self, default=True):
        o_ids = self.get_obligations(default=default)
        return (
            Company.objects.filter(obligation__id__in=o_ids).all()
        )

    def dispatch(self, request, *args, **kwargs):
        # if request.user and not request.user.obligations.count():
        #     messages.warning(
        #         request, _('You have no obligations assigned to this user')
        #     )
        return super(CompanyMixin, self).dispatch(request, *args, **kwargs)
