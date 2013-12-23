from haddock import AuthenticationFailed



class DefaultHaddockAuthenticator(object):

    def auth_usernameAndPassword(self, username, password, endpoint, params):
        
        raise AuthenticationFailed("Incorrect username or password.")
