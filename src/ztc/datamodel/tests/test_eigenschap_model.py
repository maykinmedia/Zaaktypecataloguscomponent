from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone


from ..models import Eigenschap

from .factories import (
    EigenschapFactory, EigenschapReferentieFactory, EigenschapSpecificatieFactory
)


class EigenschapModelTests(TestCase):
    def test_model_raises_error_when_both_specificatie_and_referentie_are_set(self):
        specificatie = EigenschapSpecificatieFactory.create()
        referentie = EigenschapReferentieFactory.create()

        eigenschap = EigenschapFactory.create(
            specificatie_van_eigenschap=specificatie,
            referentie_naar_eigenschap=referentie,
        )

        self.assertRaises(ValidationError, eigenschap.clean)

    def test_model_raises_error_when_both_fields_are_not_set(self):
        eigenschap = EigenschapFactory.create(
            specificatie_van_eigenschap=None,
            referentie_naar_eigenschap=None,
        )

        self.assertRaises(ValidationError, eigenschap.clean)

    def test_model_does_not_raise_an_error_when_only_specificatie_is_set(self):
        specificatie = EigenschapSpecificatieFactory.create()

        eigenschap = EigenschapFactory.create(
            specificatie_van_eigenschap=specificatie,
        )

        self.assertIsNone(eigenschap.clean())

    def test_model_does_not_raise_an_error_when_only_referentie_is_set(self):
        referentie = EigenschapReferentieFactory.create()

        eigenschap = EigenschapFactory.create(
            referentie_naar_eigenschap=referentie,
        )

        self.assertIsNone(eigenschap.clean())
