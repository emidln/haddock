from haddock import AuthenticationFailed
from twisted.internet.defer import succeed


class InMemoryStringSharedSecretSource(object):

    def __init__(self, users):
        self.users = users

    def getUserDetails(self, username):

        for user in self.users:
            if user.get("username") == username:
                return succeed(user)

        raise AuthenticationFailed("Authentication failed.")



class DummySharedSecretSource(object):

    def getUserDetails(self, username):
        raise AuthenticationFailed("Not a real authenticator.")



class DefaultHaddockAuthenticator(object):

    def __init__(self, sharedSecretSource):
        """
        Initialise the Haddock Authenticator.
        """
        self.sharedSecretSource = sharedSecretSource


    def _getUserDetails(self, username):

        if self.sharedSecretSource:
            d = self.sharedSecretSource.getUserDetails(username)
            return d
        else:
            raise AuthenticationFailed("No Authentication Backend")


    def auth_usernameAndPassword(self, username, password, endpoint, params):

        def _continue(result):
            
            if result.get("username") == username and result.get("password") == password:
                return True

            raise AuthenticationFailed("Authentication failed.")

        d = self._getUserDetails(username)
        d.addCallback(_continue)
        return d


    def auth_usernameAndHMAC(self, username, HMAC, endpoint, params):

        d = self._getUserDetails(username)
        d.addCallback(_continue)
        return d
