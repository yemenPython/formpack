# coding: utf-8

from __future__ import (unicode_literals, print_function,
                        absolute_import, division)

import unittest
import json
import xlrd

from textwrap import dedent

from collections import OrderedDict

from nose.tools import raises

from path import tempdir

from formpack import FormPack
from .fixtures import build_fixture

from formpack.constants import UNTRANSLATED

customer_satisfaction = build_fixture('customer_satisfaction')
restaurant_profile = build_fixture('restaurant_profile')


class TestFormPackExport(unittest.TestCase):
    maxDiff = None

    def assertTextEqual(self, text1, text2):
        self.assertEquals(dedent(text1).strip(), dedent(text2).strip())

    def test_generator_export(self):

        title, schemas, submissions = customer_satisfaction

        forms = FormPack(schemas, title)
        export = forms.export().to_dict(submissions)
        expected = OrderedDict({
                    "Customer Satisfaction": {
                        'fields': ["restaurant_name", "customer_enjoyment"],
                        'data': [
                            ["Felipes", "yes"],
                            ["Dunkin Donuts", "no"],
                            ["McDonalds", "no"]
                        ]
                    }
               })

        self.assertEqual(export, expected)

    def test_generator_export_labels_without_translations(self):

        title, schemas, submissions = customer_satisfaction
        fp = FormPack(schemas, title)

        self.assertEqual(len(fp[0].translations), 1)

        export = fp.export(lang=UNTRANSLATED).to_dict(submissions)
        expected = OrderedDict({
                    "Customer Satisfaction": {
                        'fields': ["Restaurant name",
                                   "Did you enjoy your dining experience?"],
                        'data': [
                            ["Felipes", "Yes"],
                            ["Dunkin Donuts", "No"],
                            ["McDonalds", "No"]
                        ]
                    }
               })

        self.assertDictEqual(export, expected)

    def test_generator_export_translation_headers(self):

        title, schemas, submissions = restaurant_profile
        fp = FormPack(schemas, title)

        self.assertEqual(len(fp.versions), 4)
        self.assertEqual(len(fp[1].translations), 2)

        # by default, exports use the question 'name' attribute
        headers = fp.export(versions=0).to_dict(submissions)['Restaurant profile']['fields']
        self.assertEquals(headers, ['restaurant_name',
                                     'location',
                                     '_location_latitude',
                                     '_location_longitude',
                                     '_location_altitude',
                                     '_location_precision'])

        # the first translation in the list is the translation that
        # appears first in the column list. in this case, 'label::english'
        translations = fp[1].translations
        export = fp.export(lang=translations[0], versions=1)
        data = export.to_dict(submissions)
        headers = data['Restaurant profile']['fields']
        self.assertEquals(headers, ['restaurant name',
                                    'location',
                                    '_location_latitude',
                                    '_location_longitude',
                                    '_location_altitude',
                                    '_location_precision'])

        export = fp.export(lang=translations[1], versions=1)
        data = export.to_dict(submissions)
        headers = data['Restaurant profile']['fields']
        self.assertEquals(headers, ['nom du restaurant',
                                    'lieu',
                                    '_lieu_latitude',
                                    '_lieu_longitude',
                                    '_lieu_altitude',
                                    '_lieu_precision'])

        # TODO: make a separate test to test to test __getitem__
        export = fp.export(lang=UNTRANSLATED, versions='rpv1')
        data = export.to_dict(submissions)
        headers = data['Restaurant profile']['fields']
        self.assertEquals(headers, ['restaurant name',
                                    'location',
                                    '_location_latitude',
                                    '_location_longitude',
                                    '_location_altitude',
                                    '_location_precision'])

    def test_export_with_choice_lists(self):

        title, schemas, submissions = restaurant_profile

        fp = FormPack(schemas, title)
        self.assertEqual(len(fp[1].translations), 2)
        # by default, exports use the question 'name' attribute
        options = {'versions': 'rpV3'}

        export = fp.export(**options).to_dict(submissions)['Restaurant profile']
        self.assertEquals(export['fields'], ['restaurant_name',
                                             'location',
                                             '_location_latitude',
                                             '_location_longitude',
                                             '_location_altitude',
                                             '_location_precision',
                                             'eatery_type'])
        self.assertEquals(export['data'], [['Taco Truck',
                                             '13.42 -25.43',
                                             '13.42',
                                             '-25.43',
                                             '',
                                             '',
                                             'takeaway'],
                                            ['Harvest',
                                             '12.43 -24.53',
                                             '12.43',
                                             '-24.53',
                                             '',
                                             '',
                                             'sit_down']])

        # if a language is passed, fields with available translations
        # are translated into that language
        options['lang'] = fp[1].translations[0]
        export = fp.export(**options).to_dict(submissions)['Restaurant profile']
        self.assertEquals(export['data'], [['Taco Truck',
                                             '13.42 -25.43',
                                             '13.42',
                                             '-25.43',
                                             '',
                                             '',
                                             'take-away'],
                                            ['Harvest',
                                             '12.43 -24.53',
                                             '12.43',
                                             '-24.53',
                                             '',
                                             '',
                                             'sit down']])

        options['lang'] = fp[1].translations[1]
        export = fp.export(**options).to_dict(submissions)['Restaurant profile']
        self.assertEquals(export['data'], [['Taco Truck',
                                             '13.42 -25.43',
                                             '13.42',
                                             '-25.43',
                                             '',
                                             '',
                                             'avec vente à emporter'],
                                            ['Harvest',
                                             '12.43 -24.53',
                                             '12.43',
                                             '-24.53',
                                             '',
                                             '',
                                             'traditionnel']])


    def test_headers_of_group_exports(self):
        title, schemas, submissions = build_fixture('grouped_questions')
        fp = FormPack(schemas, title)
        options = {'versions': 'gqs'}

        # by default, groups are stripped.
        export = fp.export(**options).to_dict(submissions)
        headers = export['Grouped questions']['fields']
        self.assertEquals(headers, ['q1', 'g1q1', 'g1sg1q1',
                                    'g1q2', 'g2q1', 'qz'])

    def test_headers_of_translated_group_exports(self):
        title, schemas, submissions = build_fixture('grouped_translated')
        fp = FormPack(schemas, title)
        options = {
            'versions': 'grouped_translated_v1', 'hierarchy_in_labels': True}
        english_export = fp.export(lang='English', **options).to_dict(
            submissions)
        self.assertEquals(
            english_export[title]['fields'],
            [
                'start',
                'end',
                'External Characteristics/What kind of symmetry do you have?',
                'External Characteristics/What kind of symmetry do you have?/Spherical',
                'External Characteristics/What kind of symmetry do you have?/Radial',
                'External Characteristics/What kind of symmetry do you have?/Bilateral',
                'External Characteristics/How many segments does your body have?',
                'Do you have body fluids that occupy intracellular space?',
                'Do you descend from an ancestral unicellular organism?',
            ]
        )
        spanish_export = fp.export(lang='Español', **options).to_dict(
            submissions)
        self.assertEquals(
            spanish_export[title]['fields'],
            [
                'start',
                'end',
                'Características externas/¿Qué tipo de simetría tiene?',
                'Características externas/¿Qué tipo de simetría tiene?/Esférico',
                'Características externas/¿Qué tipo de simetría tiene?/Radial',
                'Características externas/¿Qué tipo de simetría tiene?/Bilateral',
                'Características externas/¿Cuántos segmentos tiene tu cuerpo?',
                '¿Tienes fluidos corporales que ocupan espacio intracelular?',
                '¿Desciende de un organismo unicelular ancestral?',
            ]
        )

    def assertDictEquals(self, arg1, arg2):
        _j = lambda arg: json.dumps(arg, indent=4, sort_keys=True)
        assert _j(arg1) == _j(arg2)

    def test_submissions_of_group_exports(self):
        title, schemas, submissions = build_fixture('grouped_questions')
        fp = FormPack(schemas, title)
        options = {'versions': 'gqs'}

        export = fp.export(**options).to_dict(submissions)['Grouped questions']
        self.assertDictEquals(export['fields'], ['q1', 'g1q1', 'g1sg1q1',
                                             'g1q2', 'g2q1', 'qz'])
        self.assertDictEquals(export['data'], [['respondent1\'s r1',
                                            'respondent1\'s r2',
                                            'respondent1\'s r2.5',
                                            'respondent1\'s r2.75 :)',
                                            'respondent1\'s r3',
                                            'respondent1\'s r4'],
                                           ['respondent2\'s r1',
                                            'respondent2\'s r2',
                                            'respondent2\'s r2.5',
                                            'respondent2\'s r2.75 :)',
                                            'respondent2\'s r3',
                                            'respondent2\'s r4']])

        options['hierarchy_in_labels'] = '/'
        export = fp.export(**options).to_dict(submissions)['Grouped questions']
        self.assertDictEquals(export['fields'], ['q1',
                                             'g1/g1q1',
                                             'g1/sg1/g1sg1q1',
                                             'g1/g1q2',
                                             'g2/g2q1',
                                             'qz'])
        self.assertDictEquals(export['data'], [['respondent1\'s r1',
                                            'respondent1\'s r2',
                                            'respondent1\'s r2.5',
                                            'respondent1\'s r2.75 :)',
                                            'respondent1\'s r3',
                                            'respondent1\'s r4'],
                                           ['respondent2\'s r1',
                                            'respondent2\'s r2',
                                            'respondent2\'s r2.5',
                                            'respondent2\'s r2.75 :)',
                                            'respondent2\'s r3',
                                            'respondent2\'s r4']])

    def test_repeats(self):
        title, schemas, submissions = build_fixture('grouped_repeatable')
        fp = FormPack(schemas, title)
        options = {'versions': 'rgv1'}
        export = fp.export(**options).to_dict(submissions)
        self.assertEqual(export, OrderedDict([
                            ('Household survey with repeatable groups',
                                {
                                    'fields': [
                                        'start',
                                        'end',
                                        'household_location',
                                        '_index'
                                    ],
                                    'data': [
                                        [
                                            '2016-03-14T14:15:48.000-04:00',
                                            '2016-03-14T14:18:35.000-04:00',
                                            'montreal',
                                            1
                                        ],
                                        [
                                            '2016-03-14T14:14:10.000-04:00',
                                            '2016-03-14T14:15:48.000-04:00',
                                            'marseille',
                                            2
                                        ],
                                        [
                                            '2016-03-14T14:13:53.000-04:00',
                                            '2016-03-14T14:14:10.000-04:00',
                                            'rocky mountains',
                                            3
                                        ],
                                        [
                                            '2016-03-14T14:12:54.000-04:00',
                                            '2016-03-14T14:13:53.000-04:00',
                                            'toronto',
                                            4
                                        ],
                                        [
                                            '2016-03-14T14:18:35.000-04:00',
                                            '2016-03-14T15:19:20.000-04:00',
                                            'new york',
                                            5
                                        ],
                                        [
                                            '2016-03-14T14:11:25.000-04:00',
                                            '2016-03-14T14:12:03.000-04:00',
                                            'boston',
                                            6
                                        ]
                                    ]
                                }),
                            ('houshold_member_repeat',
                                {
                                    'fields': [
                                        'household_member_name',
                                        '_parent_table_name',
                                        '_parent_index'
                                    ],
                                    'data': [
                                        [
                                            'peter',
                                            'Household survey with repeatable groups',
                                            1
                                        ],
                                        [
                                            'kyle',
                                            'Household survey with repeatable groups',
                                            2
                                        ],
                                        [
                                            'linda',
                                            'Household survey with repeatable groups',
                                            2
                                        ],
                                        [
                                            'morty',
                                            'Household survey with repeatable groups',
                                            3
                                        ],
                                        [
                                            'tony',
                                            'Household survey with repeatable groups',
                                            4
                                        ],
                                        [
                                            'mary',
                                            'Household survey with repeatable groups',
                                            4
                                        ],
                                        [
                                            'emma',
                                            'Household survey with repeatable groups',
                                            5
                                        ],
                                        [
                                            'parker',
                                            'Household survey with repeatable groups',
                                            5
                                        ],
                                        [
                                            'amadou',
                                            'Household survey with repeatable groups',
                                            6
                                        ],
                                        [
                                            'esteban',
                                            'Household survey with repeatable groups',
                                            6
                                        ],
                                        [
                                            'suzie',
                                            'Household survey with repeatable groups',
                                            6
                                        ],
                                        [
                                            'fiona',
                                            'Household survey with repeatable groups',
                                            6
                                        ],
                                        [
                                            'phillip',
                                            'Household survey with repeatable groups',
                                            6
                                        ]
                                    ]
                                })
                            ])
        )


    def test_nested_repeats(self):
        title, schemas, submissions = build_fixture(
            'nested_grouped_repeatable')
        fp = FormPack(schemas, title)
        export_dict = fp.export(versions='bird_nests_v1').to_dict(submissions)
        expected_dict = OrderedDict([
            ('Bird nest survey with nested repeatable groups', {
                'fields': [
                    'start',
                    'end',
                    '_index'
                ],
                'data': [
                    [
                        '2017-12-27T15:53:26.000-05:00',
                        '2017-12-27T15:58:20.000-05:00',
                        1
                    ],
                    [
                        '2017-12-27T15:58:20.000-05:00',
                        '2017-12-27T15:58:50.000-05:00',
                        2
                    ]
                ]
            }),
            ('group_tree', {
                'fields': [
                    'What_kind_of_tree_is_this',
                    '_index',
                    '_parent_table_name',
                    '_parent_index'
                ],
                'data': [
                    [
                        'pine',
                        1,
                        'Bird nest survey with nested repeatable groups',
                        1
                    ],
                    [
                        'spruce',
                        2,
                        'Bird nest survey with nested repeatable groups',
                        1
                    ],
                    [
                        'maple',
                        3,
                        'Bird nest survey with nested repeatable groups',
                        2
                    ]
                ]
            }),
            ('group_nest', {
                'fields': [
                    'How_high_above_the_ground_is_the_nest',
                    'How_many_eggs_are_in_the_nest',
                    '_index',
                    '_parent_table_name',
                    '_parent_index'
                ],
                'data': [
                    [
                        '13',
                        '3',
                        1,
                        'group_tree',
                        1
                    ],
                    [
                        '15',
                        '1',
                        2,
                        'group_tree',
                        1
                    ],
                    [
                        '10',
                        '2',
                        3,
                        'group_tree',
                        2
                    ],
                    [
                        '23',
                        '1',
                        4,
                        'group_tree',
                        3
                    ]
                ]
            }),
            ('group_egg', {
                'fields': [
                    'Describe_the_egg',
                    '_parent_table_name',
                    '_parent_index'
                ],
                'data': [
                    [
                        'brown and speckled; medium',
                        'group_nest',
                        1
                    ],
                    [
                        'brown and speckled; large; cracked',
                        'group_nest',
                        1
                    ],
                    [
                        'light tan; small',
                        'group_nest',
                        1
                    ],
                    [
                        'cream-colored',
                        'group_nest',
                        2
                    ],
                    [
                        'reddish-brown; medium',
                        'group_nest',
                        3
                    ],
                    [
                        'reddish-brown; small',
                        'group_nest',
                        3
                    ],
                    [
                        'grey and speckled',
                        'group_nest',
                        4
                    ]
                ]
            })
        ])
        self.assertEqual(export_dict, expected_dict)


    def test_repeats_alias(self):
        title, schemas, submissions = build_fixture('grouped_repeatable_alias')
        fp = FormPack(schemas, title)
        options = {'versions': 'rgv1'}
        export = fp.export(**options).to_dict(submissions)

        self.assertEqual(export, OrderedDict ([
                            ('Grouped Repeatable Alias',
                                {
                                    'fields': [
                                        'start',
                                        'end',
                                        'household_location',
                                        '_index'
                                    ],
                                    'data': [
                                        [
                                            '2016-03-14T14:15:48.000-04:00',
                                            '2016-03-14T14:18:35.000-04:00',
                                            'montreal',
                                            1
                                        ],
                                        [
                                            '2016-03-14T14:14:10.000-04:00',
                                            '2016-03-14T14:15:48.000-04:00',
                                            'marseille',
                                            2
                                        ],
                                        [
                                            '2016-03-14T14:13:53.000-04:00',
                                            '2016-03-14T14:14:10.000-04:00',
                                            'rocky mountains',
                                            3
                                        ],
                                        [
                                            '2016-03-14T14:12:54.000-04:00',
                                            '2016-03-14T14:13:53.000-04:00',
                                            'toronto',
                                            4
                                        ],
                                        [
                                            '2016-03-14T14:18:35.000-04:00',
                                            '2016-03-14T15:19:20.000-04:00',
                                            'new york',
                                            5
                                        ],
                                        [
                                            '2016-03-14T14:11:25.000-04:00',
                                            '2016-03-14T14:12:03.000-04:00',
                                            'boston',
                                            6
                                        ]
                                    ]
                                }),
                            ('houshold_member_repeat',
                                {
                                    'fields': [
                                        'household_member_name',
                                        '_parent_table_name',
                                        '_parent_index'
                                    ],
                                    'data': [
                                        [
                                            'peter',
                                            'Grouped Repeatable Alias',
                                            1
                                        ],
                                        [
                                            'kyle',
                                            'Grouped Repeatable Alias',
                                            2
                                        ],
                                        [
                                            'linda',
                                            'Grouped Repeatable Alias',
                                            2
                                        ],
                                        [
                                            'morty',
                                            'Grouped Repeatable Alias',
                                            3
                                        ],
                                        [
                                            'tony',
                                            'Grouped Repeatable Alias',
                                            4
                                        ],
                                        [
                                            'mary',
                                            'Grouped Repeatable Alias',
                                            4
                                        ],
                                        [
                                            'emma',
                                            'Grouped Repeatable Alias',
                                            5
                                        ],
                                        [
                                            'parker',
                                            'Grouped Repeatable Alias',
                                            5
                                        ],
                                        [
                                            'amadou',
                                            'Grouped Repeatable Alias',
                                            6
                                        ],
                                        [
                                            'esteban',
                                            'Grouped Repeatable Alias',
                                            6
                                        ],
                                        [
                                            'suzie',
                                            'Grouped Repeatable Alias',
                                            6
                                        ],
                                        [
                                            'fiona',
                                            'Grouped Repeatable Alias',
                                            6
                                        ],
                                        [
                                            'phillip',
                                            'Grouped Repeatable Alias',
                                            6
                                        ]
                                    ]
                                })
                            ])
        )

    def test_substitute_xml_names_for_missing_labels(self):
        title, schemas, submissions = build_fixture('grouped_translated')

        # Remove a choice's labels
        self.assertEqual(
            schemas[0]['content']['choices'][0]['label'],
            ['Spherical', 'Esférico'],
        )
        del schemas[0]['content']['choices'][0]['label']

        # Remove a group's labels
        self.assertEqual(
            schemas[0]['content']['survey'][2]['label'],
            ['External Characteristics', 'Características externas'],
        )
        del schemas[0]['content']['survey'][2]['label']

        # Remove a grouped question's labels
        self.assertEqual(
            schemas[0]['content']['survey'][4]['label'],
            ['How many segments does your body have?',
             '¿Cuántos segmentos tiene tu cuerpo?'],
        )
        del schemas[0]['content']['survey'][4]['label']

        # Remove a non-grouped question's labels
        self.assertEqual(
            schemas[0]['content']['survey'][6]['label'],
            ['Do you have body fluids that occupy intracellular space?',
             '¿Tienes fluidos corporales que ocupan espacio intracelular?'],
        )
        del schemas[0]['content']['survey'][6]['label']

        fp = FormPack(schemas, title)
        options = {
            'versions': 'grouped_translated_v1', 'hierarchy_in_labels': True}

        # Missing labels should be replaced with XML names
        english_export = fp.export(lang='English', **options).to_dict(
            submissions)
        self.assertEqual(
            english_export[title]['fields'],
            [
                'start',
                'end',
                'external_characteristics/What kind of symmetry do you have?',
                'external_characteristics/What kind of symmetry do you have?/spherical',
                'external_characteristics/What kind of symmetry do you have?/Radial',
                'external_characteristics/What kind of symmetry do you have?/Bilateral',
                'external_characteristics/How_many_segments_does_your_body_have',
                'Do_you_have_body_flu_intracellular_space',
                'Do you descend from an ancestral unicellular organism?',
            ]
        )
        self.assertEqual(
            english_export[title]['data'][0][2],
            'spherical Radial Bilateral'
        )
        spanish_export = fp.export(lang='Español', **options).to_dict(
            submissions)
        self.assertEqual(
            spanish_export[title]['fields'],
            [
                'start',
                'end',
                'external_characteristics/¿Qué tipo de simetría tiene?',
                'external_characteristics/¿Qué tipo de simetría tiene?/spherical',
                'external_characteristics/¿Qué tipo de simetría tiene?/Radial',
                'external_characteristics/¿Qué tipo de simetría tiene?/Bilateral',
                'external_characteristics/How_many_segments_does_your_body_have',
                'Do_you_have_body_flu_intracellular_space',
                '¿Desciende de un organismo unicelular ancestral?',
            ]
        )
        self.assertEqual(
            spanish_export[title]['data'][0][2],
            'spherical Radial Bilateral'
        )

    def test_substitute_xml_names_for_missing_translations(self):
        title, schemas, submissions = build_fixture('grouped_translated')

        # Remove a choice's translation
        self.assertEqual(
            schemas[0]['content']['choices'][0]['label'],
            ['Spherical', 'Esférico'],
        )
        schemas[0]['content']['choices'][0]['label'] = [
            'Spherical', UNTRANSLATED]

        # Remove a group's translation
        self.assertEqual(
            schemas[0]['content']['survey'][2]['label'],
            ['External Characteristics', 'Características externas'],
        )
        schemas[0]['content']['survey'][2]['label'] = [
            'External Characteristics', UNTRANSLATED]

        # Remove a grouped question's translation
        self.assertEqual(
            schemas[0]['content']['survey'][4]['label'],
            ['How many segments does your body have?',
             '¿Cuántos segmentos tiene tu cuerpo?'],
        )
        schemas[0]['content']['survey'][4]['label'] = [
            'How many segments does your body have?', UNTRANSLATED]

        # Remove a non-grouped question's translation
        self.assertEqual(
            schemas[0]['content']['survey'][6]['label'],
            ['Do you have body fluids that occupy intracellular space?',
             '¿Tienes fluidos corporales que ocupan espacio intracelular?'],
        )
        schemas[0]['content']['survey'][6]['label'] = [
            'Do you have body fluids that occupy intracellular space?',
            UNTRANSLATED
        ]

        fp = FormPack(schemas, title)
        options = {
            'versions': 'grouped_translated_v1', 'hierarchy_in_labels': True}

        # All the English translations should still be present
        english_export = fp.export(lang='English', **options).to_dict(
            submissions)
        self.assertEqual(
            english_export[title]['fields'],
            [
                'start',
                'end',
                'External Characteristics/What kind of symmetry do you have?',
                'External Characteristics/What kind of symmetry do you have?/Spherical',
                'External Characteristics/What kind of symmetry do you have?/Radial',
                'External Characteristics/What kind of symmetry do you have?/Bilateral',
                'External Characteristics/How many segments does your body have?',
                'Do you have body fluids that occupy intracellular space?',
                'Do you descend from an ancestral unicellular organism?',
            ]
        )
        self.assertEqual(
            english_export[title]['data'][0][2],
            'Spherical Radial Bilateral'
        )

        # Missing Spanish translations should be replaced with XML names
        spanish_export = fp.export(lang='Español', **options).to_dict(
            submissions)
        self.assertEqual(
            spanish_export[title]['fields'],
            [
                'start',
                'end',
                'external_characteristics/¿Qué tipo de simetría tiene?',
                'external_characteristics/¿Qué tipo de simetría tiene?/spherical',
                'external_characteristics/¿Qué tipo de simetría tiene?/Radial',
                'external_characteristics/¿Qué tipo de simetría tiene?/Bilateral',
                'external_characteristics/How_many_segments_does_your_body_have',
                'Do_you_have_body_flu_intracellular_space',
                '¿Desciende de un organismo unicelular ancestral?',
            ]
        )
        self.assertEqual(
            spanish_export[title]['data'][0][2],
            'spherical Radial Bilateral'
        )

    def test_csv(self):
        title, schemas, submissions = build_fixture('grouped_questions')
        fp = FormPack(schemas, title)
        options = {'versions': 'gqs'}
        csv_data = "\n".join(fp.export(**options).to_csv(submissions))

        expected = """
        "q1";"g1q1";"g1sg1q1";"g1q2";"g2q1";"qz"
        "respondent1's r1";"respondent1's r2";"respondent1's r2.5";"respondent1's r2.75 :)";"respondent1's r3";"respondent1's r4"
        "respondent2's r1";"respondent2's r2";"respondent2's r2.5";"respondent2's r2.75 :)";"respondent2's r3";"respondent2's r4"
        """

        self.assertTextEqual(csv_data, expected)

        options = {'versions': 'gqs', 'hierarchy_in_labels': True}
        csv_data = "\n".join(fp.export(**options).to_csv(submissions))

        expected = """
        "q1";"g1/g1q1";"g1/sg1/g1sg1q1";"g1/g1q2";"g2/g2q1";"qz"
        "respondent1's r1";"respondent1's r2";"respondent1's r2.5";"respondent1's r2.75 :)";"respondent1's r3";"respondent1's r4"
        "respondent2's r1";"respondent2's r2";"respondent2's r2.5";"respondent2's r2.75 :)";"respondent2's r3";"respondent2's r4"
        """

        self.assertTextEqual(csv_data, expected)

        options = {'versions': 'gqs', 'hierarchy_in_labels': True,
                   'lang': UNTRANSLATED}
        csv_data = "\n".join(fp.export(**options).to_csv(submissions))

        expected = """
        "Q1";"Group 1/G1Q1";"Group 1/Sub Group 1/G1SG1Q1";"Group 1/G1Q2";"g2/G2Q1";"QZed"
        "respondent1's r1";"respondent1's r2";"respondent1's r2.5";"respondent1's r2.75 :)";"respondent1's r3";"respondent1's r4"
        "respondent2's r1";"respondent2's r2";"respondent2's r2.5";"respondent2's r2.75 :)";"respondent2's r3";"respondent2's r4"
        """
        self.assertTextEqual(csv_data, expected)

        title, schemas, submissions = restaurant_profile
        fp = FormPack(schemas, title)
        options = {'versions': 'rpV3', 'lang': fp[1].translations[1]}
        csv_data = "\n".join(fp.export(**options).to_csv(submissions))

        expected = """
        "nom du restaurant";"lieu";"_lieu_latitude";"_lieu_longitude";"_lieu_altitude";"_lieu_precision";"type de restaurant"
        "Taco Truck";"13.42 -25.43";"13.42";"-25.43";"";"";"avec vente à emporter"
        "Harvest";"12.43 -24.53";"12.43";"-24.53";"";"";"traditionnel"
        """

        self.assertTextEqual(csv_data, expected)

    def test_csv_with_tag_headers(self):
        title, schemas, submissions = build_fixture('dietary_needs')
        fp = FormPack(schemas, title)
        options = {'versions': 'dietv1', 'tag_cols_for_header': ['hxl']}
        rows = list(fp.export(**options).to_csv(submissions))
        assert rows[1] == (u'"#loc+name";"#indicator+diet";'
                           u'"#indicator+diet";"#indicator+diet";'
                           u'"#indicator+diet";"#indicator+diet"')

    # disabled for now
    # @raises(RuntimeError)
    # def test_csv_on_repeatable_groups(self):
    #     title, schemas, submissions = build_fixture('grouped_repeatable')
    #     fp = FormPack(schemas, title)
    #     options = {'versions': 'rgv1'}
    #     list(fp.export(**options).to_csv(submissions))

    def test_export_with_split_fields(self):
        title, schemas, submissions = restaurant_profile
        fp = FormPack(schemas, title)
        options = {'versions': 'rpV4'}
        export = fp.export(**options).to_dict(submissions)['Restaurant profile']
        expected = {
            'fields': [
                'restaurant_name',
                'location',
                '_location_latitude',
                '_location_longitude',
                '_location_altitude',
                '_location_precision',
                'eatery_type',
                'eatery_type/sit_down',
                'eatery_type/takeaway',
            ],
            'data': [
                [
                    'Taco Truck',
                    '13.42 -25.43',
                    '13.42',
                    '-25.43',
                    '',
                    '',
                    'takeaway sit_down',
                    '1',
                    '1'
                ],
                [
                    'Harvest',
                    '12.43 -24.53',
                    '12.43',
                    '-24.53',
                    '',
                    '',
                    'sit_down',
                    '1',
                    '0'
                ],
                [
                    'Wololo',
                    '12.43 -24.54 1 0',
                    '12.43',
                    '-24.54',
                    '1',
                    '0',
                    '',
                    '0',
                    '0'
                ],
                [
                    'Los pollos hermanos',
                    '12.43 -24.54 1',
                    '12.43',
                    '-24.54',
                    '1',
                    '',
                    '',
                    '',
                    ''
                ]
            ]
        }

        self.assertEqual(export, expected)

        options = {'versions': 'rpV4', "group_sep": "::",
                    'hierarchy_in_labels': True,
                   "lang": fp[-1].translations[1]}
        export = fp.export(**options).to_dict(submissions)['Restaurant profile']

        expected = {
            'fields': [
                'nom du restaurant',
                'lieu',
                '_lieu_latitude',
                '_lieu_longitude',
                '_lieu_altitude',
                '_lieu_precision',
                'type de restaurant',
                'type de restaurant::traditionnel',
                'type de restaurant::avec vente à emporter',
            ],
            'data': [
                [
                    'Taco Truck',
                    '13.42 -25.43',
                    '13.42',
                    '-25.43',
                    '',
                    '',
                    'avec vente à emporter traditionnel',
                    '1',
                    '1'
                ],
                [
                    'Harvest',
                    '12.43 -24.53',
                    '12.43',
                    '-24.53',
                    '',
                    '',
                    'traditionnel',
                    '1',
                    '0'
                ],
                [
                    'Wololo',
                    '12.43 -24.54 1 0',
                    '12.43',
                    '-24.54',
                    '1',
                    '0',
                    '',
                    '0',
                    '0'
                ],
                [
                    'Los pollos hermanos',
                    '12.43 -24.54 1',
                    '12.43',
                    '-24.54',
                    '1',
                    '',
                    '',
                    '',
                    ''
                ]
            ]
        }

        self.assertEqual(export, expected)

    def test_xlsx(self):
        title, schemas, submissions = build_fixture('grouped_repeatable')
        fp = FormPack(schemas, title)
        options = {'versions': 'rgv1'}

        with tempdir() as d:
            xls = d / 'foo.xlsx'
            fp.export(**options).to_xlsx(xls, submissions)
            assert xls.isfile()

    def test_xlsx_long_sheet_names_and_invalid_chars(self):
        title, schemas, submissions = build_fixture('long_names')
        fp = FormPack(schemas, title)
        options = {'versions': 'long_survey_name__the_quick__brown_fox_jumps'
                               '_over_the_lazy_dog_v1'}

        with tempdir() as d:
            xls = d / 'foo.xlsx'
            fp.export(**options).to_xlsx(xls, submissions)
            assert xls.isfile()
            book = xlrd.open_workbook(xls)
            assert book.sheet_names() == [
                u'long survey name_ the quick,...',
                u'long_group_name__Victor_jagt...',
                u'long_group_name__Victor_... (1)'
            ]


    def test_xlsx_with_tag_headers(self):
        title, schemas, submissions = build_fixture('hxl_grouped_repeatable')
        fp = FormPack(schemas, title)
        options = {'versions': 'hxl_rgv1', 'tag_cols_for_header': ['hxl']}
        with tempdir() as d:
            xls = d / 'foo.xlsx'
            fp.export(**options).to_xlsx(xls, submissions)
            assert xls.isfile()
            book = xlrd.open_workbook(xls)
            # Verify main sheet
            sheet = book.sheet_by_name('Household survey with HXL an...')
            row_values = [cell.value for cell in sheet.row(1)]
            assert row_values == [
                u'#date+start', u'#date+end', u'#loc+name', u'']
            # Verify repeating group
            sheet = book.sheet_by_name('houshold_member_repeat')
            row_values = [cell.value for cell in sheet.row(1)]
            assert row_values == [u'#beneficiary', u'', u'']

    def test_force_index(self):
        title, schemas, submissions = customer_satisfaction

        forms = FormPack(schemas, title)
        export = forms.export(force_index=True).to_dict(submissions)
        expected = OrderedDict({
                    "Customer Satisfaction": {
                        'fields': ["restaurant_name", "customer_enjoyment",
                                   "_index"],
                        'data': [
                            ["Felipes", "yes", 1],
                            ["Dunkin Donuts", "no", 2],
                            ["McDonalds", "no", 3]
                        ]
                    }
               })

        self.assertEqual(export, expected)

    def test_copy_fields(self):
        title, schemas, submissions = customer_satisfaction

        forms = FormPack(schemas, title)
        export = forms.export(copy_fields=('_uuid', '_submission_time'))
        exported = export.to_dict(submissions)
        expected = OrderedDict({
                    "Customer Satisfaction": {
                        'fields': ["restaurant_name", "customer_enjoyment",
                                   "_uuid", "_submission_time"],
                        'data': [
                            [
                                "Felipes",
                                "yes",
                                "90dd7750f83011e590707c7a9125d07d",
                                "2016-04-01 19:57:45.306805"
                            ],

                            [
                                "Dunkin Donuts",
                                "no",
                                "90dd7750f83011e590707c7a9125d08d",
                                "2016-04-02 19:57:45.306805"
                            ],

                            [
                                "McDonalds",
                                "no",
                                "90dd7750f83011e590707c7a9125d09d",
                                "2016-04-03 19:57:45.306805"
                            ]
                        ]
                    }
               })

        self.assertDictEquals(exported, expected)

    def test_copy_fields_and_force_index_and_unicode(self):
        title, schemas, submissions = customer_satisfaction

        fp = FormPack(schemas, 'رضا العملاء')
        export = fp.export(copy_fields=('_uuid', '_submission_time'),
                              force_index=True)
        exported = export.to_dict(submissions)
        expected = OrderedDict({
                    "رضا العملاء": {
                        'fields': ["restaurant_name", "customer_enjoyment",
                                   "_uuid", "_submission_time", "_index"],
                        'data': [
                            [
                                "Felipes",
                                "yes",
                                "90dd7750f83011e590707c7a9125d07d",
                                "2016-04-01 19:57:45.306805",
                                1
                            ],

                            [
                                "Dunkin Donuts",
                                "no",
                                "90dd7750f83011e590707c7a9125d08d",
                                "2016-04-02 19:57:45.306805",
                                2
                            ],

                            [
                                "McDonalds",
                                "no",
                                "90dd7750f83011e590707c7a9125d09d",
                                "2016-04-03 19:57:45.306805",
                                3
                            ]
                        ]
                    }
               })

        self.assertEqual(exported, expected)

        with tempdir() as d:
            xls = d / 'test.xlsx'
            fp.export().to_xlsx(xls, submissions)
            assert xls.isfile()

    def test_copy_fields_multiple_versions(self):
        title, schemas, submissions = restaurant_profile

        forms = FormPack(schemas, title)
        export = forms.export(
            versions=forms.versions,
            copy_fields=('_uuid',)
        )
        exported = export.to_dict(submissions)
        expected = OrderedDict({
            'Restaurant profile': {
                'fields': ['restaurant_name', 'location', '_location_latitude',
                           '_location_longitude', '_location_altitude',
                           '_location_precision', 'eatery_type',
                           'eatery_type/sit_down', 'eatery_type/takeaway', '_uuid'],
                'data': [
                    [
                        'Felipes',
                        '12.34 -23.45',
                        '12.34',
                        '-23.45',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '5dd6ecda-b993-42fc-95c2-7856a8940acf',
                    ],

                    [
                        'Felipes',
                        '12.34 -23.45',
                        '12.34',
                        '-23.45',
                        '',
                        '',
                        '',
                        '',
                        '',
                        'd6dee2e1-e0e6-4d08-9ad4-d78d77079f85',
                    ],

                    [
                        'Taco Truck',
                        '13.42 -25.43',
                        '13.42',
                        '-25.43',
                        '',
                        '',
                        'takeaway',
                        '',
                        '',
                        '3f2ac742-305a-4b0d-b7ef-f7f57fcd14dc',
                    ],

                    [
                        'Harvest',
                        '12.43 -24.53',
                        '12.43',
                        '-24.53',
                        '',
                        '',
                        'sit_down',
                        '',
                        '',
                        '3195b926-1578-4bac-80fc-735129a34090',
                    ],

                    [
                        'Taco Truck',
                        '13.42 -25.43',
                        '13.42',
                        '-25.43',
                        '',
                        '',
                        'takeaway sit_down',
                        '1',
                        '1',
                        '04cbcf32-ecbd-4801-829b-299463dcd125',
                    ],

                    [
                        'Harvest',
                        '12.43 -24.53',
                        '12.43',
                        '-24.53',
                        '',
                        '',
                        'sit_down',
                        '1',
                        '0',
                        '1f21b881-db1d-4629-9b82-f4111630187d',
                    ],

                    [
                        'Wololo',
                        '12.43 -24.54 1 0',
                        '12.43',
                        '-24.54',
                        '1',
                        '0',
                        '',
                        '0',
                        '0',
                        'fda7e49b-6c84-4cfe-b1a8-3de997ac0880',
                    ],

                    [
                        'Los pollos hermanos',
                        '12.43 -24.54 1',
                        '12.43',
                        '-24.54',
                        '1',
                        '',
                        '',
                        '',
                        '',
                        'a4277940-c8f3-4564-ad3b-14e28532a976',
                    ]
                ]
            }
        })

        self.assertDictEquals(exported, expected)

    def test_choices_external_as_text_field(self):
        title, schemas, submissions = build_fixture('sanitation_report_external')

        fp = FormPack(schemas, title)
        export = fp.export(lang=UNTRANSLATED)
        exported = export.to_dict(submissions)
        expected = OrderedDict([
                    (
                        'Sanitation report external', {
                            'fields': [
                                'Restaurant name',
                                'How did this restaurant do on its sanitation report?',
                                'Report date'
                            ],
                            'data': [
                                [
                                    'Felipes',
                                    'A',
                                    '012345'
                                ],
                                [
                                    'Chipotle',
                                    'C',
                                    '012346'
                                ],
                                [
                                    'Dunkin Donuts',
                                    'D',
                                    '012347'
                                ],
                                [
                                    'Boloco',
                                    'B',
                                    '012348'
                                ]
                            ]
                        }
                    )
                ])

        self.assertEqual(exported, expected)

    def test_headers_of_multi_version_exports(self):
        title, schemas, submissions = build_fixture('site_inspection')
        fp = FormPack(schemas, title)
        export = fp.export(versions=fp.versions.keys()).to_dict(submissions)
        headers = export['Site inspection']['fields']
        self.assertListEqual(headers, [
            'inspector',
            'did_you_find_the_site',
            'was_there_damage_to_the_site',
            'ping',
            'was_there_damage_to_the_site_dupe',
            'rssi',
            'is_the_gate_secure',
            'is_plant_life_encroaching',
            'please_rate_the_impact_of_any_defects_observed',
        ])

    def test_literacy_test_export(self):
        title, schemas, submissions = build_fixture('literacy_test')
        fp = FormPack(schemas, title)
        export = fp.export(versions=fp.versions.keys()).to_dict(submissions)
        headers = export['Literacy test']['fields']
        expected_headers = (
            [
                 'russian_passage_1/Word at flash',
                 'russian_passage_1/Duration of exercise',
                 'russian_passage_1/Total words attempted',
                 'russian_passage_1',
            ] + ['russian_passage_1/' + str(i) for i in range(1, 47)] + [
                 'russian_passage_2/Word at flash',
                 'russian_passage_2/Duration of exercise',
                 'russian_passage_2/Total words attempted',
                 'russian_passage_2',
            ] + ['russian_passage_2/' + str(i) for i in range(1, 47)]
        )
        self.assertListEqual(headers, expected_headers)
        expected_data = [
            [
                # Word at flash, duration of exercise, total words attempted
                '22', '16', '46',
                # Incorrect words as list in single column
                '1 2 4 8 10 19 20 21 29 30 33 39 46',
                # Incorrect words as binary values in separate columns
                '1', '1', '0', '1', '0', '0', '0', '1', '0', '1', '0', '0',
                '0', '0', '0', '0', '0', '0', '1', '1', '1', '0', '0', '0',
                '0', '0', '0', '0', '1', '1', '0', '0', '1', '0', '0', '0',
                '0', '0', '1', '0', '0', '0', '0', '0', '0', '1',
                # All the same for the  second literacy test question
                '21', '9', '46',
                '1 5 14 16 30 32 39',
                '1', '0', '0', '0', '1', '0', '0', '0', '0', '0', '0', '0',
                '0', '1', '0', '1', '0', '0', '0', '0', '0', '0', '0', '0',
                '0', '0', '0', '0', '0', '1', '0', '1', '0', '0', '0', '0',
                '0', '0', '1', '0', '0', '0', '0', '0', '0', '0',
            ], [
                '46', '14', '46',
                '1 2 3 4 5 6 7 8 9',
                '1', '1', '1', '1', '1', '1', '1', '1', '1', '0', '0', '0',
                '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
                '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
                '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
                '45', '7', '46',
                '1 11 29 46',
                '1', '0', '0', '0', '0', '0', '0', '0', '0', '0', '1', '0',
                '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
                '0', '0', '0', '0', '1', '0', '0', '0', '0', '0', '0', '0',
                '0', '0', '0', '0', '0', '0', '0', '0', '0', '1',
            ], [
                '9', '12', '46',
                '1 2 3 4 6 7 8',
                '1', '1', '1', '1', '0', '1', '1', '1', '0', '0', '0', '0',
                '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
                '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
                '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
                '33', '7', '36',
                '1 11 20 30 32',
                '1', '0', '0', '0', '0', '0', '0', '0', '0', '0', '1', '0',
                '0', '0', '0', '0', '0', '0', '0', '1', '0', '0', '0', '0',
                '0', '0', '0', '0', '0', '1', '0', '1', '0', '0', '0', '0',
                '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
            ],
        ]
        self.assertListEqual(
            export['Literacy test']['data'],
            expected_data
        )
