$(function () {

    $('table[data-toggle=datatable]').customDataTable();

    $('.filter_data').on('change', function () {
        var val = $(this).find('option:selected').text();
        var index = $(this).data('column-index')
        dt.fnFilter(val, index);
    });

});
