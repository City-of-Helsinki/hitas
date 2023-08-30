import datetime
import json

import pytest
from auditlog.models import LogEntry
from django.contrib.contenttypes.models import ContentType

from hitas.models import Owner, SurfaceAreaPriceCeilingCalculationData
from hitas.models.utils import deobfuscate
from hitas.tests.factories import OwnerFactory


@pytest.mark.django_db
def test_activity_log__create():
    activity_log: list[LogEntry] = list(LogEntry.objects.all())
    assert len(activity_log) == 0

    owner: Owner = OwnerFactory.create(name="Testi Testinen", identifier="123456-789A", email="testi@testinen.fi")

    activity_log: list[LogEntry] = list(LogEntry.objects.all())
    assert len(activity_log) == 1
    assert activity_log[0].content_type == ContentType.objects.get_for_model(Owner)
    assert activity_log[0].object_pk == str(owner.pk)
    assert activity_log[0].action == LogEntry.Action.CREATE
    assert json.loads(activity_log[0].changes) == {
        "id": ["None", str(owner.id)],
        "valid_identifier": ["None", str(owner.valid_identifier)],
        "ownerships": ["None", "hitas.Ownership.None"],
        "deleted_by_cascade": ["None", str(owner.deleted_by_cascade)],
        "email": ["None", "*" * len(owner.email)],
        "name": ["None", "*" * len(owner.name)],
        "uuid": ["None", str(owner.uuid)],
        "identifier": ["None", "*" * len(owner.identifier)],
        "bypass_conditions_of_sale": ["None", str(owner.bypass_conditions_of_sale)],
        "non_disclosure": ["None", str(owner.non_disclosure)],
    }


@pytest.mark.django_db
def test_activity_log__update():
    activity_log: list[LogEntry] = list(LogEntry.objects.all())
    assert len(activity_log) == 0

    owner: Owner = OwnerFactory.create(name="Testi Testinen 1", identifier="123456-789A")
    owner.name = "Testi Testinen 2"
    owner.save()

    activity_log: list[LogEntry] = list(LogEntry.objects.filter(action=LogEntry.Action.UPDATE).all())
    assert len(activity_log) == 1
    assert activity_log[0].content_type == ContentType.objects.get_for_model(Owner)
    assert activity_log[0].object_pk == str(owner.pk)
    assert activity_log[0].action == LogEntry.Action.UPDATE
    assert json.loads(activity_log[0].changes) == {
        "name": ["*" * len("Testi Testinen 1"), "*" * len("Testi Testinen 2")],
    }


@pytest.mark.django_db
def test_activity_log__soft_delete(freezer):
    freezer.move_to("2023-01-01 00:00:00")
    activity_log: list[LogEntry] = list(LogEntry.objects.all())
    assert len(activity_log) == 0

    owner: Owner = OwnerFactory.create(name="Testi Testinen", identifier="123456-789A")

    # Create logs for soft deletes
    owner.delete()
    activity_log: list[LogEntry] = list(LogEntry.objects.filter(action=LogEntry.Action.DELETE).all())
    assert len(activity_log) == 1
    assert activity_log[0].content_type == ContentType.objects.get_for_model(Owner)
    assert activity_log[0].object_pk == str(owner.pk)
    assert activity_log[0].action == LogEntry.Action.DELETE
    # Soft delete doesn't actually delete the object, but due to how the auditlog works,
    # the changes are recorded like this.
    assert json.loads(activity_log[0].changes) == {
        "id": [str(owner.id), "None"],
        "valid_identifier": [str(owner.valid_identifier), "None"],
        "deleted": ["2023-01-01 00:00:00", "None"],
        "ownerships": ["hitas.Ownership.None", "None"],
        "deleted_by_cascade": [str(owner.deleted_by_cascade), "None"],
        "email": ["*" * len(owner.email), "None"],
        "name": ["*" * len(owner.name), "None"],
        "uuid": [str(owner.uuid), "None"],
        "identifier": ["*" * len(owner.identifier), "None"],
        "bypass_conditions_of_sale": [str(owner.bypass_conditions_of_sale), "None"],
        "non_disclosure": [str(owner.non_disclosure), "None"],
    }

    # Create logs for undeletes
    owner.undelete()
    activity_log: list[LogEntry] = list(LogEntry.objects.filter(action=LogEntry.Action.UPDATE).all())
    assert len(activity_log) == 1
    assert activity_log[0].content_type == ContentType.objects.get_for_model(Owner)
    assert activity_log[0].object_pk == str(owner.pk)
    assert activity_log[0].action == LogEntry.Action.UPDATE
    # Changes here are also not recorded correctly due to how auditlog works.
    assert json.loads(activity_log[0].changes) == {
        "deleted": ["None", "2023-01-01 00:00:00"],
    }


@pytest.mark.django_db
def test_activity_log__delete():
    activity_log: list[LogEntry] = list(LogEntry.objects.all())
    assert len(activity_log) == 0

    data: SurfaceAreaPriceCeilingCalculationData = SurfaceAreaPriceCeilingCalculationData.objects.create(
        calculation_month=datetime.date(2021, 1, 1),
        data={"foo": "1"},
    )
    data_pk = str(data.pk)
    data.delete()

    activity_log: list[LogEntry] = list(LogEntry.objects.filter(action=LogEntry.Action.DELETE).all())
    assert len(activity_log) == 1
    assert activity_log[0].content_type == ContentType.objects.get_for_model(SurfaceAreaPriceCeilingCalculationData)
    assert activity_log[0].object_pk == data_pk
    assert activity_log[0].action == LogEntry.Action.DELETE
    assert json.loads(activity_log[0].changes) == {
        "calculation_month": ["2021-01-01", "None"],
        "data": ["{'foo': '1'}", "None"],
    }


@pytest.mark.django_db
def test_activity_log__bulk_create():
    activity_log: list[LogEntry] = list(LogEntry.objects.all())
    assert len(activity_log) == 0

    Owner.objects.bulk_create(
        objs=[
            Owner(name="Testi Testinen 1", identifier="123456-789A"),
            Owner(name="Testi Testinen 2", identifier="123456-789B"),
        ],
    )

    activity_log: list[LogEntry] = list(LogEntry.objects.all())
    assert len(activity_log) == 2
    assert activity_log[0].content_type == ContentType.objects.get_for_model(Owner)
    assert activity_log[0].action == LogEntry.Action.CREATE
    assert activity_log[1].content_type == ContentType.objects.get_for_model(Owner)
    assert activity_log[1].action == LogEntry.Action.CREATE


@pytest.mark.django_db
def test_activity_log__bulk_update():
    activity_log: list[LogEntry] = list(LogEntry.objects.all())
    assert len(activity_log) == 0

    owner_1: Owner = OwnerFactory.create(name="Testi Testinen 1", identifier="123456-789A")
    owner_2: Owner = OwnerFactory.create(name="Testi Testinen 2", identifier="123456-789B")

    owner_1.name = "Testi Testinen 1.1"
    owner_2.name = "Testi Testinen 2.1"

    Owner.objects.bulk_update([owner_1, owner_2], fields=["name"])

    activity_log: list[LogEntry] = list(LogEntry.objects.filter(action=LogEntry.Action.UPDATE).all())
    assert len(activity_log) == 2
    assert activity_log[0].content_type == ContentType.objects.get_for_model(Owner)
    assert activity_log[0].action == LogEntry.Action.UPDATE
    assert activity_log[1].content_type == ContentType.objects.get_for_model(Owner)
    assert activity_log[1].action == LogEntry.Action.UPDATE


@pytest.mark.django_db
def test_activity_log__qs_update():
    activity_log: list[LogEntry] = list(LogEntry.objects.all())
    assert len(activity_log) == 0

    owner_1: Owner = OwnerFactory.create(name="Testi Testinen 1", identifier="123456-789A")
    owner_2: Owner = OwnerFactory.create(name="Testi Testinen 2", identifier="123456-789B")

    Owner.objects.filter(pk__in=[owner_1.pk, owner_2.pk]).update(identifier=None)

    activity_log: list[LogEntry] = list(LogEntry.objects.filter(action=LogEntry.Action.UPDATE).all())
    assert len(activity_log) == 2
    assert activity_log[0].content_type == ContentType.objects.get_for_model(Owner)
    assert activity_log[0].action == LogEntry.Action.UPDATE
    assert activity_log[1].content_type == ContentType.objects.get_for_model(Owner)
    assert activity_log[1].action == LogEntry.Action.UPDATE


@pytest.mark.django_db
def test_activity_log__qs_soft_delete():
    activity_log: list[LogEntry] = list(LogEntry.objects.all())
    assert len(activity_log) == 0

    owner_1: Owner = OwnerFactory.create(name="Testi Testinen 1", identifier="123456-789A")
    owner_2: Owner = OwnerFactory.create(name="Testi Testinen 2", identifier="123456-789B")

    Owner.objects.filter(pk__in=[owner_1.pk, owner_2.pk]).delete()

    activity_log: list[LogEntry] = list(LogEntry.objects.filter(action=LogEntry.Action.DELETE).all())
    assert len(activity_log) == 2
    assert activity_log[0].content_type == ContentType.objects.get_for_model(Owner)
    assert activity_log[0].action == LogEntry.Action.DELETE
    assert activity_log[1].content_type == ContentType.objects.get_for_model(Owner)
    assert activity_log[1].action == LogEntry.Action.DELETE


@pytest.mark.django_db
def test_activity_log__qs_delete():
    activity_log: list[LogEntry] = list(LogEntry.objects.all())
    assert len(activity_log) == 0

    data_1: SurfaceAreaPriceCeilingCalculationData = SurfaceAreaPriceCeilingCalculationData.objects.create(
        calculation_month=datetime.date(2021, 1, 1),
        data={"foo": "1"},
    )
    data_2: SurfaceAreaPriceCeilingCalculationData = SurfaceAreaPriceCeilingCalculationData.objects.create(
        calculation_month=datetime.date(2022, 1, 1),
        data={"bar": "2"},
    )

    SurfaceAreaPriceCeilingCalculationData.objects.filter(pk__in=[data_1.pk, data_2.pk]).delete()

    activity_log: list[LogEntry] = list(LogEntry.objects.filter(action=LogEntry.Action.DELETE).all())
    assert len(activity_log) == 2
    assert activity_log[0].content_type == ContentType.objects.get_for_model(SurfaceAreaPriceCeilingCalculationData)
    assert activity_log[0].action == LogEntry.Action.DELETE
    assert activity_log[1].content_type == ContentType.objects.get_for_model(SurfaceAreaPriceCeilingCalculationData)
    assert activity_log[1].action == LogEntry.Action.DELETE


@pytest.mark.django_db
def test_activity_log__obfuscated_owner():
    # Create obfuscated owner
    owner_0: Owner = OwnerFactory.create(
        name="Testi Testinen",
        identifier="123456-789A",
        email=None,
        non_disclosure=True,
    )

    # Owner is obfuscated immediately after it has been saved
    assert owner_0.name == ""
    assert owner_0.identifier is None
    assert owner_0.email is None

    # Obfuscated values should be stored in _obfuscated_data
    assert owner_0._unobfuscated_data == {"name": "Testi Testinen", "identifier": "123456-789A", "email": None}

    # Fetch obfuscated owner
    owner_1: Owner = Owner.objects.first()

    # Access obfuscated owner fields, which should be obfuscated
    assert owner_1.name == ""
    assert owner_1.identifier is None
    assert owner_1.email is None

    # Obfuscated values should be stored in _obfuscated_data
    assert owner_1._unobfuscated_data == {"name": "Testi Testinen", "identifier": "123456-789A", "email": None}

    # Triggering save should work
    owner_1.save()

    # The current instance should still be obfuscated
    assert owner_1.name == ""
    assert owner_1.identifier is None
    assert owner_1.email is None
    assert owner_1._unobfuscated_data == {"name": "Testi Testinen", "identifier": "123456-789A", "email": None}

    # Obfuscated values should not have been saved to the database, but the owner is still obfuscated when accessed
    owner_2: Owner = Owner.objects.first()
    assert owner_2.name == ""
    assert owner_2.identifier is None
    assert owner_2.email is None
    assert owner_2._unobfuscated_data == {"name": "Testi Testinen", "identifier": "123456-789A", "email": None}

    # So far, no access logs should have been created
    access_logs: list[LogEntry] = list(LogEntry.objects.filter(action=LogEntry.Action.ACCESS).all())
    assert len(access_logs) == 0

    # Manually de-obfuscating the owner should create an access log for this owner
    obfuscated_data = deobfuscate(owner_2)
    access_logs: list[LogEntry] = list(LogEntry.objects.filter(action=LogEntry.Action.ACCESS).all())
    assert len(access_logs) == 1
    assert access_logs[0].content_type == ContentType.objects.get_for_model(Owner)
    assert access_logs[0].object_pk == str(owner_2.pk)

    # This is the data that was used to obfuscate the owner
    assert obfuscated_data == {"name": "", "identifier": None, "email": None}
