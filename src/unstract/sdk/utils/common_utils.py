import uuid


class CommonUtils:
    @staticmethod
    def get_uuid() -> str:
        """Class method to get uuid."""
        return str(uuid.uuid4())
