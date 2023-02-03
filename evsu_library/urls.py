from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('', include('system.urls', namespace='system')),
    # {% url 'admin:polls_choice_add' %}
    # path('admin/system/outgoingtransaction/add/'),
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
