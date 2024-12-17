import os
import time
import uuid
from typing import Any

from redis import StrictRedis


class MetricsMixin:
    TIME_TAKEN_KEY = "time_taken(s)"

    def __init__(self, run_id):
        """Initialize the MetricsMixin class.

        Args:
            run_id (str): Unique identifier for the run.
        """
        self.run_id = run_id
        self.op_id = str(uuid.uuid4())  # Unique identifier for this instance

        # Initialize Redis client
        self.redis_client = StrictRedis(
            host=os.getenv("REDIS_HOST", "unstract-redis"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            username=os.getenv("REDIS_USER", "default"),
            password=os.getenv("REDIS_PASSWORD", ""),
            db=1,
            decode_responses=True,
        )
        self.redis_key = f"metrics:{self.run_id}:{self.op_id}"

        # Set the start time immediately upon initialization
        self.set_start_time()

    def set_start_time(self, ttl=86400):
        """Store the current timestamp in Redis when the instance is
        created."""
        self.redis_client.set(self.redis_key, time.time(), ex=ttl)

    def collect_metrics(self) -> dict[str, Any]:
        """Calculate the time taken since the timestamp was set and delete the
        Redis key.

        Returns:
            dict: The calculated time taken and the associated run_id and op_id.
        """
        # Check if the key exists in Redis
        if not self.redis_client.exists(self.redis_key):
            # If the key is missing, return an empty metrics dictionary
            return {self.TIME_TAKEN_KEY: None}

        start_time = float(
            self.redis_client.get(self.redis_key)
        )  # Get the stored timestamp
        time_taken = round(time.time() - start_time, 3)

        # Delete the Redis key after use
        self.redis_client.delete(self.redis_key)

        return {self.TIME_TAKEN_KEY: time_taken}
