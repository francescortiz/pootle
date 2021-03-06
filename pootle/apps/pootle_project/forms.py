#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
#
# This file is a part of the Pootle project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from django import forms
from django.utils.translation import ugettext as _

from django_rq.queues import get_queue

from pootle_language.models import Language
from pootle_misc.forms import LiberalModelChoiceField
from pootle_project.models import Project
from pootle_translationproject.models import TranslationProject


def init_tp_from_templates(tp):
    """Wraps translation project method to allow it to be running as RQ job"""
    tp.init_from_templates()


class TranslationProjectForm(forms.ModelForm):

    language = LiberalModelChoiceField(
        label=_("Language"),
        queryset=Language.objects.all(),
        widget=forms.Select(
            attrs={
                'class': 'js-select2 select2-language'}))
    project = forms.ModelChoiceField(
        queryset=Project.objects.all(),
        widget=forms.HiddenInput())

    class Meta(object):
        prefix = "existing_language"
        model = TranslationProject
        fields = ('language', 'project')

    def __init__(self, *args, **kwargs):
        """If this form is not bound, it must be called with an initial value
        for Project.
        """
        super(TranslationProjectForm, self).__init__(*args, **kwargs)
        if kwargs.get("instance"):
            project_id = kwargs["instance"].project.pk
        else:
            project_id = kwargs["initial"]["project"]
            self.fields["language"].queryset = (
                self.fields["language"].queryset.exclude(
                    translationproject__project_id=project_id))
        self.fields["project"].queryset = self.fields[
            "project"].queryset.filter(pk=project_id)

    def save(self, commit=True):
        tp = self.instance
        initialize_from_templates = False
        if tp.id is None:
            initialize_from_templates = tp.can_be_inited_from_templates()

        tp = super(TranslationProjectForm, self).save(commit)
        if initialize_from_templates:
            queue = get_queue('default')
            queue.enqueue(init_tp_from_templates, tp)

        return tp
