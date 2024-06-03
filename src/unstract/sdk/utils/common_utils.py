import uuid


class CommonUtils:
    @staticmethod
    def generate_uuid() -> str:
        """Class method to get uuid."""
        return str(uuid.uuid4())
