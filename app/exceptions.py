class NoneServices(Exception):
    """Raised when no services found in the database"""
    def __init__(self):
        super().__init__("No services found!")


class NoneProjects(Exception):
    """Raised when no projects found in database"""
    def __init__(self):
        super().__init__("No projects found!")


class IdNotExists(Exception):
    """ Will be thrown when the queried id was not found """
    pass


class MissingStructure(Exception):
    """ Will be thrown when a requested structure does not exist in redis """
    pass


class MissingAttribute(Exception):
    """ Will be thrown when a requested attribute does not exist in a service"""
    pass


class APIResponseFormatException(Exception):
    """ Will be thrown when the api response does not have the excepted structure"""
    pass


class APIResponseError(Exception):
    """ Will be thrown when an api request has a status different from 200 or 404"""
    pass


class ModeDoesNotExist(Exception):
    """
    Will be thrown when the mode parameter passed in is not recognised.
    Current modes allowed:
        * PORTAL-RECOMMENDER
        * PROVIDERS-RECOMMENDER
        * SIMILAR_SERVICES_EVALUATION
    """
    pass


class MethodDoesNotExist(Exception):
    """
    Will be thrown when the method parameter given is not supported.
    """
    pass


class NoTextAttributes(Exception):
    """
    Will be thrown when no text attributes are provided in the config and the mode running requires them,
    e.g. autocompletion
    """
    pass


class DeprecatedMethod(Exception):
    """
    Will be thrown when a method not used anymore is picked in the config
    """
    pass


class RegistryMethodNotImplemented(Exception):
    """
    Will be thrown when a registry method not implemented is called
    """
    pass
