import unittest
from scripts.c2_bpat_ferc714_pudl_glue_csv_pinned_audit import (
    git_blob_sha1, inspect, BLOB, COMMIT, URL,
)

class TestPublishedFERCCrossEraIdentity(unittest.TestCase):
    def test_git_blob_known_vector(self):
        self.assertEqual(git_blob_sha1(b"hello"), "b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0")

    def test_wrong_source_rejected(self):
        with self.assertRaisesRegex(ValueError, "identity mismatch"):
            inspect(b"fabricated mapping")

    def test_source_and_commit_are_immutable(self):
        self.assertEqual(len(BLOB), 40)
        self.assertIn(COMMIT, URL)
        self.assertNotIn("nightly", URL)

if __name__ == "__main__":
    unittest.main()
