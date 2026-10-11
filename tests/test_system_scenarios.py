import unittest
from benchmark_system_4_2 import run_system_benchmark
class SystemScenarios(unittest.TestCase):
    def test_twenty_isolated_outcomes(self):
        outcomes=run_system_benchmark()
        self.assertEqual(20,len(outcomes))
        for result in outcomes:
            with self.subTest(scenario=result['scenario']):
                self.assertTrue(result['score']['passed'],result)
