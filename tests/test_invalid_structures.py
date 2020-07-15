# coding: utf-8
from __future__ import (unicode_literals, print_function,
                        absolute_import, division)

import unittest
from copy import copy

from nose.tools import raises

from formpack import FormPack

SINGLE_NOTE_SURVEY = {'content': {
        'survey': [
            {'type': 'note', 'label': 'Note', 'name': 'note'}
        ]
    }}


class TestInvalidCases(unittest.TestCase):

    def test_single_version_doesnt_require_version(self):
        FormPack(id_string="idstring", versions=[
                copy(SINGLE_NOTE_SURVEY),
            ])

    @raises(ValueError)
    def test_conflicting_version_ids(self):
        FormPack(id_string="idstring", versions=[
                copy(SINGLE_NOTE_SURVEY),
                copy(SINGLE_NOTE_SURVEY),
            ])

    @raises(TypeError)
    def test_formpack_cannot_have_name(self):
        vdata = copy(SINGLE_NOTE_SURVEY)
        FormPack(id_string="idstring",
                 name="somename",
                 versions=[
                     vdata,
                 ])
