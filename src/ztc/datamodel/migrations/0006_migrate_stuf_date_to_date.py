# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-05-17 12:56
from __future__ import unicode_literals

from django.db import migrations
from django.db.models import Func, F, Q, Value
from django.db.models.functions import ConcatPair

MODELS = [
    'BesluitType',
    'Eigenschap',
    'InformatieObjecttype',
    'InformatieObjectTypeOmschrijvingGeneriek',
    'ResultaatType',
    'RolType',
    'StatusType',
    'ZaakObjectType',
    'ZaakType',
]

class ToDate(Func):
    function = 'to_date'


class ToChar(Func):
    function = 'to_char'


def forward(apps, schema_editor):
    for model in MODELS:
        ModelClass = apps.get_model('datamodel', model)

        conflicts = ModelClass.objects.exclude(datum_begin_geldigheid__istartswith='V')
        if conflicts.count():
            raise ValueError('Expected all "datum_begin_geldigheid" to start with a "V" in "{}". Check PKs: {}'.format(
                model, ', '.join(map(str, conflicts.values_list('pk', flat=True)))))

        conflicts = ModelClass.objects.exclude(Q(datum_einde_geldigheid=None) | Q(datum_einde_geldigheid__istartswith='V'))
        if conflicts.count():
            raise ValueError('Expected all "datum_einde_geldigheid" to start with a "V" in "{}". Check PKs: {}'.format(
                model, ', '.join(map(str, conflicts.values_list('pk', flat=True)))))

        ModelClass.objects.update(
            datum_begin_geldigheid_new=ToDate(F('datum_begin_geldigheid'), Value('?YYYYMMDD')),
        )

        ModelClass.objects.exclude(datum_einde_geldigheid=None).update(
            datum_einde_geldigheid_new=ToDate(F('datum_einde_geldigheid'), Value('?YYYYMMDD')),
        )

    ZaakType = apps.get_model('datamodel', 'ZaakType')
    ZaakType.objects.update(versiedatum_new=ToDate(F('versiedatum'), Value('YYYYMMDD')))


def backward(apps, schema_editor):
    for model in MODELS:
        ModelClass = apps.get_model('datamodel', model)

        ModelClass.objects.update(
            datum_begin_geldigheid=ConcatPair(Value('V'), ToChar(F('datum_begin_geldigheid_new'), Value('YYYYMMDD'))),
        )

        ModelClass.objects.exclude(datum_einde_geldigheid_new=None).update(
            datum_einde_geldigheid=ConcatPair(Value('V'), ToChar(F('datum_einde_geldigheid_new'), Value('YYYYMMDD'))),
        )

    ZaakType = apps.get_model('datamodel', 'ZaakType')
    ZaakType.objects.update(versiedatum=ToChar(F('versiedatum_new'), Value('YYYYMMDD')))


class Migration(migrations.Migration):

    dependencies = [
        ('datamodel', '0005_auto_20180517_1455'),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]