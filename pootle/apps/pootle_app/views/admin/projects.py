#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
#
# This file is a part of the Pootle project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from django.views.generic import TemplateView

from pootle.core.utils.json import jsonify
from pootle.core.views import APIView, SuperuserRequiredMixin
from pootle_app.forms import ProjectForm
from pootle_language.models import Language
from pootle_project.models import Project
from pootle_store.filetypes import filetype_choices


__all__ = ('ProjectAdminView', 'ProjectAPIView')


class ProjectAdminView(SuperuserRequiredMixin, TemplateView):
    template_name = 'admin/projects.html'

    def get_context_data(self, **kwargs):
        languages = Language.objects.exclude(code='templates')
        language_choices = [(lang.id, unicode(lang)) for lang in languages]
        try:
            english = Language.objects.get(code='en')
            default_language = english.id
        except Language.DoesNotExist:
            default_language = languages[0].id

        return {
            'page': 'admin-projects',
            'form_choices': jsonify({
                'checkstyle': Project.checker_choices,
                'localfiletype': filetype_choices,
                'source_language': language_choices,
                'treestyle': Project.treestyle_choices,
                'defaults': {
                    'source_language': default_language,
                },
            }),
        }


class ProjectAPIView(SuperuserRequiredMixin, APIView):
    model = Project
    base_queryset = Project.objects.order_by('-id')
    add_form_class = ProjectForm
    edit_form_class = ProjectForm
    page_size = 10
    search_fields = ('code', 'fullname', 'disabled')
