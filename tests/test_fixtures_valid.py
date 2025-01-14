# coding: utf-8
import unittest

from formpack import FormPack
from .fixtures import build_fixture
from .fixtures.load_fixture_json import load_analysis_form_json
from formpack.constants import ANALYSIS_TYPES


class TestFormPackFixtures(unittest.TestCase):
    maxDiff = None

    def _reimport(self, fd):
        fd2 = FormPack(**fd.to_dict())
        return fd2

    def test_sanitation_report(self):
        """
        sanitation_report
        """
        title, schemas, submissions = build_fixture('sanitation_report')
        fp = FormPack(schemas, title)
        self.assertEqual(len(fp.versions), 1)
        v0 = fp[0]
        self.assertEqual(
            list(v0.sections['Sanitation report'].fields.keys()),
            ['restaurant_name', 'restaurant_rating', 'report_date'],
        )

    def test_grouped_questions(self):
        """
        questions groups
        """
        title, schemas, submissions = build_fixture('grouped_questions')
        fp = FormPack(schemas, title)
        self.assertEqual(len(fp.versions), 1)
        self.assertEqual(
            list(fp[0].sections['Grouped questions'].fields.keys()),
            ['q1', 'g1q1', 'g1sg1q1', 'g1q2', 'g2q1', 'qz'],
        )

    def test_customer_satisfaction(self):
        """
        customer_satisfaction
        """
        title, schemas, submissions = build_fixture('customer_satisfaction')
        fp = FormPack(schemas, title)
        v0 = fp[0]
        self.assertEqual(len(fp.versions), 1)
        self.assertEqual(
            list(v0.sections['Customer Satisfaction'].fields.keys()),
            ['restaurant_name', 'customer_enjoyment'],
        )
        self.assertEqual(
            sorted(fp.to_dict().keys()), ['id_string', 'title', 'versions']
        )
        # TODO: find a way to restore this test (or change fixtures)
        # self.assertEqual(fp.to_dict(), {'title': 'Customer Satisfaction',
        #                                 'id_string': 'customer_satisfaction',
        #                                 'versions': schemas})

    def test_restaurant_profile(self):
        title, schemas, submissions = build_fixture('restaurant_profile')
        fp = FormPack(schemas, title)
        self.assertEqual(len(fp.versions), 4)
        v0 = fp[0]
        self.assertEqual(
            list(v0.sections['Restaurant profile'].fields.keys()),
            ['restaurant_name', 'location'],
        )

        self.assertEqual(
            sorted(fp.to_dict().keys()),
            sorted(['id_string', 'title', 'versions']),
        )
        # TODO: find a way to restore this test (or change fixtures)
        # self.assertEqual(fp.to_dict(), {'title': 'Restaurant profile',
        #                                 'id_string': 'restaurant_profile',
        #                                 'versions': schemas})

    def test_site_inspection(self):
        title, schemas, submissions = build_fixture('site_inspection')
        fp = FormPack(schemas, title)
        self.assertEqual(len(fp.versions), 5)
        v0 = fp[0]
        self.assertEqual(
            list(v0.sections['Site inspection'].fields.keys()),
            [
                'inspector',
                'did_you_find_the_site',
                'was_there_damage_to_the_site',
                'was_there_damage_to_the_site_dupe',
                'ping',
                'rssi',
                'is_the_gate_secure',
                'is_plant_life_encroaching',
                'please_rate_the_impact_of_any_defects_observed',
            ],
        )

        self.assertEqual(
            sorted(fp.to_dict().keys()),
            sorted(['id_string', 'title', 'versions']),
        )

        self.assertEqual(
            fp.to_dict(),
            {
                'title': 'Site inspection',
                'id_string': 'site_inspection',
                'versions': [s['content'] for s in schemas],
            },
        )

    # TODO: update this test, it doesn't test anything anymore.
    def test_xml_instances_loaded(self):
        """
        favcolor has submissions_xml specified
        """
        fp = FormPack(**build_fixture('favcolor'))
        self.assertEqual(len(fp.versions), 2)

    def test_analysis_form(self):
        fixture = build_fixture('analysis_form')
        assert 3 == len(fixture)

        title, schemas, submissions = fixture
        analysis_form = load_analysis_form_json('analysis_form')
        fp = FormPack(schemas, title)
        fp.extend_survey(analysis_form)

        assert 2 == len(fp.versions)
        assert 'Simple Clerk Interaction' == title

        expected_analysis_questions = sorted(
            [f['name'] for f in analysis_form['additional_fields']]
        )
        actual_analysis_questions = sorted(
            [f.name for f in fp.analysis_form.fields]
        )
        assert expected_analysis_questions == actual_analysis_questions

        f1 = fp.analysis_form.fields[0]
        assert hasattr(f1, 'source') and f1.source
        assert hasattr(f1, 'has_stats') and not f1.has_stats
        assert (
            hasattr(f1, 'analysis_type') and f1.analysis_type in ANALYSIS_TYPES
        )
        assert hasattr(f1, 'settings')
