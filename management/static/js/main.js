$(function () {

    $('table[data-toggle=datatable]').customDataTable();

    $('.filter_data').on('change', function () {
        var selectedOption = $(this).find('option:selected');
        var index = $(this).data('column-index');
        var value = $(this).data('value') || 'val';

        if (selectedOption.val() != '') {
            var val = value == 'val' ? selectedOption.val()
                                     : selectedOption.text();
            dt.fnFilter(val, index);
        } else {
            dt.fnFilter('', index);
        }
    });

    $('.delete-link').on('click', function(e) {
        e.preventDefault();
        var userConfirmed = confirm('Are you sure?');
        if (userConfirmed) {
            $('#delete-form').submit();
        }
    });

});
