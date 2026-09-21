"""The landing site is real: the package imports and declares itself.

Deliberately thin. Reel has no runtime yet — Phase B-runtime carries it — and a
suite that asserted behaviour it does not have would be theatre. What this does
buy is a CI pipeline that is green from the first commit, so the first carried
module lands against a working harness rather than a red one.
"""
import reel


def test_package_imports_and_declares_a_version():
    assert isinstance(reel.__version__, str)
    assert reel.__version__


def test_the_fixture_seam_is_registered():
    # Phase A6: named before it is consumed, so Phase B-harness inherits a
    # contract rather than inventing one.
    assert reel.EVAL_CASES_ENV == "REEL_EVAL_CASES"


def test_the_schema_seam_is_registered():
    # The counterpart to REEL_EVAL_CASES: domain-bound tests read a schema by
    # path instead of this repo carrying one.
    assert reel.TEST_SCHEMA_ENV == "REEL_TEST_SCHEMA"
