from haddock import auth
from haddock import AuthenticationFailed

from twisted.trial import unittest


class HaddockAuthTests(unittest.TestCase):

    def test_checkForNoAuthBackend(self):

        authenticator = auth.DefaultHaddockAuthenticator(None)

        self.assertRaises(
            AuthenticationFailed, authenticator.auth_usernameAndPassword,
            "user", "pass", "", {})


    def test_inMemoryStringSharedSecretSourcePassword(self):

        def _catch(res):
            self.assertIsInstance(res.value, AuthenticationFailed)

        users = [
            {
                "username": "bob",
                "password": "42"
            },
            {
                "username": "alice",
                "canonicalUsername": "alice@houseofcar.ds",
                "password": "wonderland"
            }
        ]

        authenticator = auth.DefaultHaddockAuthenticator(
            auth.InMemoryStringSharedSecretSource(users))

        authDeferred = authenticator.auth_usernameAndPassword(
            "alice", "wonderland", None, None)
        authDeferred.addCallback(self.assertEqual, "alice@houseofcar.ds")
        authDeferred.addCallback(
            lambda _: authenticator.auth_usernameAndPassword("bob", "pass",
            None, None)).addErrback(_catch)

        return authDeferred


    def test_inMemoryStringSharedSecretSourceHMAC(self):

        self.skipTest("HMAC isn't implemented yet.")

        def _catch(res):
            self.assertIsInstance(res.value, AuthenticationFailed)

        users = [
            {
                "username": "bob",
                "password": "42"
            },
            {
                "username": "alice",
                "password": "wonderland"
            }
        ]

        authenticator = auth.DefaultHaddockAuthenticator(
            auth.InMemoryStringSharedSecretSource(users))

        authDeferred = authenticator.auth_usernameAndHMAC(
            "alice", "this is not a hmac", None, {}).addErrback(_catch)

        return authDeferred
