from haddock import AuthenticationFailed



class DefaultHaddockAuthenticator(object):

    def auth_usernameAndPassword(self, username, password):
        
        raise AuthenticationFailed("Incorrect username or password.")

    def auth_usernameAndHMAC(self, username, HMAC):
        
        raise AuthenticationFailed("Incorrect username or HMAC.")