"""Control-plane enforcement tests, not source-string presence checks."""
from test_red_team_4_3 import run_red_team_pass
def run_security_regression():
    return run_red_team_pass()
if __name__=='__main__':
    raise SystemExit(0 if run_security_regression().wasSuccessful() else 1)
