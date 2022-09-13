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
