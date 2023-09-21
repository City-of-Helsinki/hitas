from auditlog.models import LogEntry
from factory.django import DjangoModelFactory


class LogEntryFactory(DjangoModelFactory):
    class Meta:
        model = LogEntry
