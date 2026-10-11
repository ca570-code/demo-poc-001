import unittest

import benchmark_runner as br


class TransformEdgeCaseTests(unittest.TestCase):
    def setUp(self):
        self._original_load = br.load

    def tearDown(self):
        br.load = self._original_load

    def _stub_load(self, records, aliases=None, pii_fields=None):
        def fake_load(name):
            if name == "DEMO-DATASET-001.json":
                return {"records": records}
            if name == "DEMO-TAXONOMY-001.json":
                return {
                    "terpene_aliases": aliases or {},
                    "pii_fields": pii_fields or [],
                }
            raise FileNotFoundError(name)

        br.load = fake_load

    def test_invalid_or_unrecognized_date_values_are_left_untouched(self):
        self._stub_load(
            [{
                "image_filename": "img-1.png",
                "created_date": "2026/99/99",
                "handwritten_header": "not-a-date",
            }],
            aliases={},
            pii_fields=[],
        )

        actual = br.transform()

        self.assertEqual(actual[0]["created_date"], "2026/99/99")
        self.assertEqual(actual[0]["handwritten_header"], "not-a-date")

    def test_unknown_terpene_aliases_are_normalized(self):
        self._stub_load(
            [{"terpenes": {"Mystery Oil": 0.42}}],
            aliases={"BETA-MYRCENE": "beta_myrcene"},
            pii_fields=[],
        )

        actual = br.transform()

        self.assertEqual(actual[0]["terpenes"]["mystery_oil"], 0.42)

    def test_missing_optional_fields_are_handled_without_crashing(self):
        self._stub_load(
            [{"customer": "Alice"}],
            aliases={},
            pii_fields=["customer"],
        )

        actual = br.transform()

        self.assertEqual(actual[0]["customer"], "[REDACTED]")
        self.assertEqual(actual[0]["source_record_index"], 0)
        self.assertIsNone(actual[0].get("image_filename"))

    def test_pii_redaction_is_applied_for_all_pii_fields(self):
        self._stub_load(
            [{
                "image_filename": "img-2.png",
                "customer": "Alice Example",
                "customer_license": "LIC-12345",
            }],
            aliases={},
            pii_fields=["customer", "customer_license"],
        )

        actual = br.transform()

        self.assertEqual(actual[0]["customer"], "[REDACTED]")
        self.assertEqual(actual[0]["customer_license"], "[REDACTED]")


if __name__ == "__main__":
    unittest.main()
