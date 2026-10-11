"""Deterministic adversarial checks; failure is a nonzero process exit."""
import unittest
def run_red_team_pass():
    suite=unittest.defaultTestLoader.loadTestsFromNames(['tests.test_security','tests.test_policy','tests.test_pipeline'])
    return unittest.TextTestRunner(verbosity=2).run(suite)
if __name__=='__main__':
    raise SystemExit(0 if run_red_team_pass().wasSuccessful() else 1)
