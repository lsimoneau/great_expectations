from great_expectations.core import ExpectationSuiteValidationResultSchema
from great_expectations.data_context.store.database_store_backend import DatabaseStoreBackend
from great_expectations.data_context.store.store import Store
from great_expectations.data_context.store.fixed_length_tuple_store_backend import FixedLengthTupleStoreBackend
from great_expectations.data_context.types import ValidationResultIdentifier
from great_expectations.data_context.util import load_class


class ValidationsStore(Store):
    _key_class = ValidationResultIdentifier

    def __init__(self, store_backend=None, runtime_environment=None):
        self._expectationSuiteValidationResultSchema = ExpectationSuiteValidationResultSchema(strict=True)

        if store_backend is not None:
            store_backend_module_name = store_backend.get("module_name", "great_expectations.data_context.store")
            store_backend_class_name = store_backend.get("class_name", "InMemoryStoreBackend")
            store_backend_class = load_class(store_backend_class_name, store_backend_module_name)

            if issubclass(store_backend_class, FixedLengthTupleStoreBackend):
                # Provide defaults for this common case
                store_backend["key_length"] = store_backend.get("key_length", 5)
                store_backend["filepath_template"] = store_backend.get("filepath_template", "{4}/{0}/{1}/{2}/{3}.json")
            elif issubclass(store_backend_class, DatabaseStoreBackend):
                # Provide defaults for this common case
                store_backend["table_name"] = store_backend.get("table_name", "ge_validations_store")
                store_backend["key_columns"] = store_backend.get(
                    "key_columns", [
                        "run_id",
                        "datasource",
                        "generator",
                        "generator_asset",
                        "expectation_suite_name"
                    ]
                )
        super(ValidationsStore, self).__init__(store_backend=store_backend, runtime_environment=runtime_environment)

    def serialize(self, key, value):
        return self._expectationSuiteValidationResultSchema.dumps(value).data

    def deserialize(self, key, value):
        return self._expectationSuiteValidationResultSchema.loads(value).data