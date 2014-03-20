$(function () {

    var table = $('table[data-toggle=datatable]');
    if(table.length > 0) {
        var columns = $.map(table.data('columns'), function (el) {
            return { sName: el };
        });
        var column_defs = table.data('column-defs') || [];
        var fnServerData = window.fnServerData || function (sSource, aoData, fnCallback) {
            $.getJSON(sSource, aoData, fnCallback);
        };
        var column_sorting = table.data('column-sorting') || [];

        window.dt = table.dataTable({
            bProcessing: true,
            bServerSide: true,
            iDisplayLength: 50,
            bLengthChange: false,
            sAjaxSource: table.data('source'),
            aoColumns: columns,
            aoColumnDefs: column_defs,
            aaSorting: column_sorting,
            fnServerData: fnServerData,
            oLanguage: {
              sProcessing: '<img src="/static/img/loading.gif" width="16" height="16" />'
            }
        });
    }

});
