""" Basic auth helpers.

$Id$
"""

def extraction( self, request ):

    """ Fetch HTTP Basic Auth credentials from the request.
    """
    creds = request._authUserPW()

    if creds is not None:
        name, password = creds

        return { 'login' : name, 'password' : password }

    return {}

def authentication( self, credentials ):

    """ Authenticate against nested acl_users.
    """
    real_user_folder = self.simple_uf.acl_users

    login = credentials.get( 'login' )
    password = credentials.get( 'password' )

    user = real_user_folder.authenticate( login, password, {} )

    return user is not None and login or None


def authorize( self, user ):

    """ Fetch user roles from nested acl_users.
    """
    real_user_folder = self.simple_uf.acl_users
    real_user = real_user_folder.getUserById( user.getId() )
    return real_user.getRoles()
