
from django.db.models import Model
from django.views.generic import View

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
