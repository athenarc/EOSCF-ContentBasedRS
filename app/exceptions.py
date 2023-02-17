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
    """ Will be thrown when a requested attribute does not exist in a resource"""
    pass


class APIResponseFormatException(Exception):
    """ Will be thrown when the api response does not have the excepted structure"""
    pass


class APIResponseError(Exception):
    """ Will be thrown when an api request has a status different than 200"""
    pass
