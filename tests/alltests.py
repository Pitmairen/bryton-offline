
import unittest


if __name__ == '__main__':


    tests = [
        'test_tcx',
    ]

    suite = unittest.TestLoader().loadTestsFromNames(tests)

    unittest.TextTestRunner().run(suite)
