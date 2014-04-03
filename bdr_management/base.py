
from django.db.models import Model
from django.views.generic import View
from django.core.exceptions import ImproperlyConfigured

from braces.views import AjaxResponseMixin, JSONResponseMixin


class FilterView(JSONResponseMixin, AjaxResponseMixin, View):

    def get_queryset(self, options):
        raise NotImplementedError

    def _process_field_value(self, value):
        if isinstance(value, Model):
            return unicode(value)
        return value

    def get_ajax(self, request):
        args = request.GET

        columns = args['sColumns'].split(',')
        limit = (int(args.get('iDisplayLength', 10)) +
                 int(args.get('iDisplayStart', 0)))
        get_rows = {
            'offset': int(args.get('iDisplayStart', 0)),
            'limit': limit,
            'count': False,
        }

        get_limit = {
            'offset': 0,
            'limit': None,
            'count': True,
        }

        with_filter = {
            'search': args.get('sSearch', ''),
            'order_by': (),
        }

        no_filter = {
            'search': '',
        }

        filters = {columns[i]: args.get('sSearch_%s' % i)
                   for i in range(len(columns)) if args.get('sSearch_%s' % i)}
        with_filter['filters'] = filters

        nr_of_sorting_cols = args.get('iSortingCols', 0)
        if nr_of_sorting_cols > 0:
            column = columns[int(args.get('iSortCol_0', 0))]
            direction = args.get('sSortDir_0', 'asc')
            with_filter['order_by'] = column
            if direction == 'desc':
                with_filter['order_by'] = '-%s' % column

        options = dict(with_filter, **get_rows)
        table_data = []
        for row in self.get_queryset(options):
            row_data = []
            for column in columns:
                callback = getattr(self, 'process_%s' % column, None)
                column_value = self._process_field_value(
                    getattr(row, column, None))
                if callback:
                    row_data.append(callback(row, column_value))
                else:
                    row_data.append(column_value)
            table_data.append(row_data)

        count_filtered = self.get_queryset(dict(with_filter, **get_limit))
        count_total = self.get_queryset(dict(no_filter, **get_limit))

        return self.render_json_response({
            'iTotalRecords': count_filtered,
            'iTotalDisplayRecords': count_total,
            'aaData': table_data,

        })


class ModelTableMixin(object):

    def get_context_data(self, **kwargs):
        context = super(ModelTableMixin, self).get_context_data(**kwargs)
        context['fields'] = self._get_model_fields()
        context['edit_url'] = self.get_edit_url()
        context['delete_url'] = self.get_delete_url()
        context['back_url'] = self.get_back_url()
        context['title'] = context.get('object', '')
        return context

    def get_edit_url(self):
        return getattr(self, 'edit_url', None)

    def get_delete_url(self):
        return getattr(self, 'delete_url', None)

    def get_back_url(self):
        return getattr(self, 'back_url', None)

    def _get_model_fields(self):
        model = getattr(self, 'model', None)
        fields = getattr(self, 'fields', [])
        exclude = getattr(self, 'exclude', [])

        if not model:
            raise ImproperlyConfigured(
                'ModelTableMixin requires a definition of model')
        model_fields = model._meta.fields
        if fields:
            model_fields = filter(lambda x: x.name in fields,
                                  model_fields)
        if exclude:
            model_fields = filter(lambda x: x.name not in exclude,
                                  model_fields)
        return model_fields


class ModelTableEditMixin(ModelTableMixin):

    template_name = 'bdr_management/_edit.html'


class ModelTableViewMixin(ModelTableMixin):

    template_name = 'bdr_management/_view.html'
