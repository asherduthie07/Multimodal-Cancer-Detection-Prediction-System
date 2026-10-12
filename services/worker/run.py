import os
import redis
from services.api.oncofusion.db import init_db
from services.api.oncofusion.main import run_job


def main():
    init_db()
    queue = redis.Redis.from_url(os.environ["REDIS_URL"])
    while True:
        entry = queue.brpop("oncofusion:jobs", timeout=5)
        if entry:
            run_job(entry[1].decode())


if __name__ == "__main__":
    main()
