
from django_assets import Bundle, register


MANAGEMENT_JS_ASSETS = (
    'js/jquery.dataTables.min.js',
    'js/jquery.customDataTable.js',
    'js/main.js',
)


MANAGEMENT_CSS_ASSETS = (
    'style.css',
    'css/jquery.dataTables.css',
    'css/jquery.dataTables_themeroller.css',
)


management_js = Bundle(*MANAGEMENT_JS_ASSETS, filters='jsmin',
                       output='management_packed.js')
management_css = Bundle(*MANAGEMENT_CSS_ASSETS, filters='cssmin',
                        output='management_packed.css')

register('management_js', management_js)
register('management_css', management_css)
