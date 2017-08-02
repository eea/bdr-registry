;(function ( $, window, document, undefined ) {

    var pluginName = 'customDataTable', defaults = {};

    function DataTable( element, options ) {
        this.element = element;
        this.$element = $(element);
        this.options = $.extend( {}, defaults, options) ;

        this._defaults = defaults;
        this._name = pluginName;

        this.init();
    }

    DataTable.prototype = {

        init: function() {
            var el = this.$element,
                columns = $.map(el.data('columns'), function (el) {
                    return { sName: el };
                }),
                column_defs = el.data('column-defs') || [],
                column_sorting = el.data('column-sorting') || [],
                table_tools = eval(el.data('tools')) || undefined;

            var options = {
                bProcessing: true,
                bServerSide: true,
                iDisplayLength: 50,
                bLengthChange: false,
                sAjaxSource: el.data('source'),
                aoColumns: columns,
                aoColumnDefs: column_defs,
                aaSorting: column_sorting,
                // fnServerData: fnServerData,
                oLanguage: {
                  sProcessing: 'Loading ...'
                }
            };
            if (table_tools) {
                options['sDom'] = 'T<"clear">lfrtip';
                options['oTableTools'] = table_tools;
            }
            window.dt = el.dataTable(options);

        }
    };

    // A really lightweight plugin wrapper around the constructor,
    // preventing against multiple instantiations
    $.fn[pluginName] = function ( options ) {
        return this.each(function () {
            if (!$.data(this, 'plugin_' + pluginName)) {
                $.data(this, 'plugin_' + pluginName,
                new DataTable( this, options ));
            }
        });
    };

})( jQuery, window, document );
