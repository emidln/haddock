from haddock import auth
from haddock import AuthenticationFailed

from twisted.trial import unittest


class HaddockAuthTests(unittest.TestCase):

    def test_checkForNoAuthBackend(self):

        authenticator = auth.DefaultHaddockAuthenticator(None)

        self.assertRaises(
            AuthenticationFailed, authenticator.auth_usernameAndPassword,
            "user", "pass", "", {})

    def test_inMemoryStringSharedSecretSource(self):

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

        authDeferred = authenticator.auth_usernameAndPassword(
            "alice", "wonderland", None, None)       
        authDeferred.addCallback(
            lambda _: authenticator.auth_usernameAndPassword("bob", "pass",
            None, None)).addErrback(_catch)

        return authDeferred
