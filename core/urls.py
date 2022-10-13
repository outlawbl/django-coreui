# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from django.urls import path, include  # add this
from django.utils.translation import gettext_lazy as _
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('admin/', admin.site.urls),          # Django admin route
    path("", include("apps.authentication.urls")), # Auth routes - login / register

    # ADD NEW Routes HERE

    # Leave `Home.Urls` as last the last line
    path('rosetta/', include('rosetta.urls')),  # NEW
    path("watcher/", include("apps.watcher.urls")),
    path("", include("apps.home.urls"))
]

urlpatterns = i18n_patterns(
    path(_('admin/'), admin.site.urls),
    path("", include("apps.authentication.urls")), # Auth routes - login / register

    # Leave `Home.Urls` as last the last line
    path(_('rosetta/'), include('rosetta.urls')),  # NEW
    path(_("watcher/"), include("apps.watcher.urls")),
    path(_(""), include("apps.home.urls"))
    )