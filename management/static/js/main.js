$(function () {

    $('table[data-toggle=datatable]').customDataTable();

    $('.filter_data').on('change', function () {
        var selectedOption = $(this).find('option:selected');
        var index = $(this).data('column-index');

        if (selectedOption.val() > 0) {
            dt.fnFilter(selectedOption.text(), index);
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
