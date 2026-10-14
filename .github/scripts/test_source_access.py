import contextlib
import importlib.util
import io
from pathlib import Path
import unittest
from unittest.mock import patch
import urllib.error

spec = importlib.util.spec_from_file_location("source_access", Path(__file__).with_name("check-source-access.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SourceAccessTests(unittest.TestCase):
    def test_checks_contents_access_without_printing_private_response(self):
        with patch("urllib.request.urlopen", return_value=io.BytesIO(b"private response")) as get, \
                contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(module.check("test-secret", "a" * 40), 0)
        request = get.call_args.args[0]
        self.assertTrue(request.full_url.endswith("/git/commits/" + "a" * 40))
        self.assertEqual(request.get_header("Authorization"), "Bearer test-secret")
        self.assertNotIn("test-secret", output.getvalue())
        self.assertNotIn("private response", output.getvalue())

    def test_fixed_actionable_errors_never_echo_remote_details(self):
        for code, message in ((401, "invalid or expired"), (403, "organization approval"),
                              (404, "resource owner CreatonDevelopment"), (500, "service status")):
            with self.subTest(code=code):
                error = urllib.error.HTTPError("private URL", code, "private error", {}, io.BytesIO(b"private body"))
                with patch("urllib.request.urlopen", side_effect=error), \
                        contextlib.redirect_stdout(io.StringIO()) as output:
                    self.assertEqual(module.check("test-secret", "a" * 40), 1)
                error.close()
                self.assertIn(message, output.getvalue())
                for private in ("test-secret", "private URL", "private error", "private body"):
                    self.assertNotIn(private, output.getvalue())

    def test_network_failure_is_sanitized(self):
        with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("private diagnostic")), \
                contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(module.check("test-secret", "a" * 40), 1)
        self.assertIn("could not reach GitHub", output.getvalue())
        self.assertNotIn("private diagnostic", output.getvalue())


if __name__ == "__main__":
    unittest.main()
