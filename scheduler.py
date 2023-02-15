from rocketry import Rocketry
from rocketry.conds import (
    every, hourly, daily,
    after_success,
    true, false, cron
)

cron_schedule = Rocketry(config={"task_execution": "async"})
      
if __name__ == "__main__":
    # If this script is run, only Rocketry is run
    cron_schedule.run()