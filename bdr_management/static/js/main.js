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

    $('#reset-filters').on('click', function(e) {
        e.preventDefault();
        $('.filter_data').each(function() {
            var optionElem = $(this);
            if (optionElem.val() != '') {
                optionElem.val('').change();
            }
        });
    });

    $('.delete-link').on('click', function(e) {
        e.preventDefault();
        var userConfirmed = confirm('Are you sure?');
        if (userConfirmed) {
            var deleteForm = $('#delete-form');
            var postUrl = $(this).attr('href');
            deleteForm.attr('action', postUrl);
            $('#delete-form').submit();
        }
    });

    $('.cancel-button').on('click', function(e) {
        e.preventDefault();
        window.location.href = $(this).data('href');
    });

    $('#organisation-filters-button').on('click', function(e) {
      $('#organisation-filters').toggleClass('hidden');
      $(this).hide();
    })

    $('#organisation-filters').on('click', function(e) {
        $('#organisation-filters').toggleClass('hidden');
        $('#organisation-filters-button').show();
    })

    $('input[name=send_mail]').on('change', function () {
        if($(this).is(':checked')) {
            $('#organisation-persons').show();
        } else {
            $('#organisation-persons').hide();
        }
    }).change();

});
