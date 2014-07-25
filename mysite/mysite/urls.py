from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from Users.forms import CustomRegistrationForm
from registration.backends.default.views import RegistrationView

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    #url(r'^Users/', include('Users.urls')),
    url(r'accounts/register/$', 
        RegistrationView.as_view(form_class = CustomRegistrationForm), 
        name = 'registration_register'),
    url(r'^accounts/', include('registration.backends.default.urls')),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
