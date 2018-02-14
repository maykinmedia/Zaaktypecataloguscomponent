from django.test import TestCase
from django.urls import reverse

from freezegun import freeze_time

from ztc.datamodel.models import Eigenschap
from ztc.datamodel.tests.base_tests import HaaglandenMixin
from ztc.datamodel.tests.factories import (
    EigenschapReferentieFactory, EigenschapSpecificatieFactory
)

from .base import ClientAPITestMixin

EIGENSCHAP_ONE_NAAM = 'Beoogd(e) product(en'
EIGENSCHAP_TWO_NAAM = 'Aard product'


@freeze_time('2018-02-07')  # datum_begin_geldigheid will be 'today': 'V20180207'
class EigenschapAPITests(ClientAPITestMixin, HaaglandenMixin, TestCase):
    maxDiff = None

    def setUp(self):
        super().setUp()

        self.eigenschap_list_url = reverse('api:eigenschap-list', kwargs={
            'version': '1',
            'catalogus_pk': self.catalogus.pk,
            'zaaktype_pk': self.zaaktype.pk
        })
        self.eigenschap_beoogde_producten_detail_url = reverse('api:eigenschap-detail', kwargs={
            'version': '1',
            'catalogus_pk': self.catalogus.pk,
            'zaaktype_pk': self.zaaktype.pk,
            'pk': self.eigenschap_beoogde_producten.pk
        })

        #
        # make a referentie for one Eigenschap, and a specificatie for the other one
        #
        self.assertEqual(Eigenschap.objects.all().count(), 2)
        self.eigenschap_one = Eigenschap.objects.get(eigenschapnaam=EIGENSCHAP_ONE_NAAM)
        self.eigenschap_two = Eigenschap.objects.get(eigenschapnaam=EIGENSCHAP_TWO_NAAM)

        specificatie = EigenschapSpecificatieFactory.create(
            kardinaliteit='1',
            lengte='1',
            groep='groep',
        )
        self.eigenschap_one.specificatie_van_eigenschap = specificatie
        self.eigenschap_one.save()

        referentie = EigenschapReferentieFactory.create(
            x_path_element='x_path_element',
            namespace='namespace',
        )
        self.eigenschap_two.referentie_naar_eigenschap = referentie
        self.eigenschap_two.save()

    def test_get_list(self):
        response = self.api_client.get(self.eigenschap_list_url)
        self.assertEqual(response.status_code, 200)

        expected = {
            '_links': {
                'self': {
                    'href': 'http://testserver/api/v1/catalogussen/{}/zaaktypen/{}/eigenschappen/'.format(
                        self.catalogus.pk, self.zaaktype.pk)}
            },
            'results':
                [
                    {
                        'ingangsdatumObject': 'V20180207',
                        'einddatumObject': None,
                        'isVan': 'http://testserver/api/v1/catalogussen/{}/zaaktypen/{}/'.format(
                            self.catalogus.pk, self.zaaktype.pk),
                        'status_type': None,
                        'naam': EIGENSCHAP_ONE_NAAM,
                        'definitie': '',
                        'toelichting': '',
                        'specificatie': {
                            'formaat': '',
                            'groep': 'groep',
                            'kardinaliteit': '1',
                            'lengte': '1',
                            'waardeverzameling': []
                        },
                        'referentie': None,
                        'url': 'http://testserver/api/v1/catalogussen/{}/zaaktypen/{}/eigenschappen/{}/'.format(
                            self.catalogus.pk, self.zaaktype.pk, self.eigenschap_one.pk),
                    },
                    {
                        'ingangsdatumObject': 'V20180207',
                        'einddatumObject': None,
                        'isVan': 'http://testserver/api/v1/catalogussen/{}/zaaktypen/{}/'.format(
                            self.catalogus.pk, self.zaaktype.pk),
                        'status_type': None,
                        'naam': EIGENSCHAP_TWO_NAAM,
                        'definitie': '',
                        'specificatie': None,
                        'toelichting': 'Nieuw / Verandering / Ambtshalve wijziging / Ontheffing / Intrekking',
                        'referentie': {
                            'pathElement': 'x_path_element',
                            'informatiemodel': None,
                            'namespace': 'namespace',
                            'entiteittype': '',
                            'schemalocatie': '',
                            'objecttype': None
                        },
                        'url': 'http://testserver/api/v1/catalogussen/{}/zaaktypen/{}/eigenschappen/{}/'.format(
                            self.catalogus.pk, self.zaaktype.pk, self.eigenschap_two.pk),
                    }
                ]
        }
        self.assertEqual(response.json(), expected)

    def test_get_detail(self):
        response = self.api_client.get(self.eigenschap_beoogde_producten_detail_url)
        self.assertEqual(response.status_code, 200)

        expected = {
            'definitie': '',
            'einddatumObject': None,
            'ingangsdatumObject': 'V20180207',
            'isVan': 'http://testserver/api/v1/catalogussen/{}/zaaktypen/{}/'.format(
                self.catalogus.pk, self.zaaktype.pk),
            'naam': 'Beoogd(e) product(en',
            'referentie': None,
            'specificatie': {'formaat': '',
                             'groep': 'groep',
                             'kardinaliteit': '1',
                             'lengte': '1',
                             'waardeverzameling': []},
            'status_type': None,
            'toelichting': '',
            'url': 'http://testserver/api/v1/catalogussen/{}/zaaktypen/{}/eigenschappen/{}/'.format(
                self.catalogus.pk, self.zaaktype.pk, self.eigenschap_beoogde_producten.pk)
        }
        self.assertEqual(expected, response.json())