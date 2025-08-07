import json

import factory
from factory import DictFactory


class JsonDict(dict):
    def json(self, **kwargs):
        return json.dumps(self, **kwargs)


class JsonableFactory(DictFactory):
    @classmethod
    def build(cls, **kwargs):
        return JsonDict(super().build(**kwargs))

    @classmethod
    def _generate(cls, strategy, params):
        """Override the core method used by `__call__()`"""
        dict_obj = super()._generate(strategy, params)
        return JsonDict(dict_obj)


class CreateSampleRecordRequestFactory(JsonableFactory):
    record_data: str = factory.Faker("text", max_nb_chars=8)
    name = factory.Faker("text", max_nb_chars=8)


class UpdateSampleRecordRequestFactory(JsonableFactory):
    id: int = factory.Faker("integer")
    record_data: str | None = factory.Faker("text", max_nb_chars=8)
    name: str | None = factory.Faker("text", max_nb_chars=8)
