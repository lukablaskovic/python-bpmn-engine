from pony.orm import *
from datetime import datetime
import env
import os
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

DB = Database()


class Event(DB.Entity):
    model_name = Required(str)
    instance_id = Required(str)
    activity_id = Required(str)
    timestamp = Required(datetime, precision=6)
    pending = Required(StrArray)
    activity_variables = Required(Json)

    def to_dict(self):
        return {
            "model_name": self.model_name,
            "instance_id": self.instance_id,
            "activity_id": self.activity_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "pending": self.pending,
            "activity_variables": self.activity_variables,
        }


class RunningInstance(DB.Entity):
    running = Required(bool)
    instance_id = Required(str, unique=True)


def setup_db():
    try:
        if not os.path.isdir("database"):
            os.mkdir("database")
            logger.info("Created database directory")
        if env.DB["provider"] == "postgres":
            DB.bind(**env.DB)
        else:
            DB.bind(
                provider="sqlite", filename="database/database.sqlite", create_db=True
            )
        DB.generate_mapping(create_tables=True)
        logger.info("Database setup completed")
    except Exception as e:
        logger.error(f"Error setting up the database: {e}")


@db_session
def add_event(
    model_name, instance_id, activity_id, timestamp, pending, activity_variables
):
    try:
        Event(
            model_name=model_name,
            instance_id=instance_id,
            activity_id=activity_id,
            timestamp=timestamp,
            pending=pending,
            activity_variables=activity_variables,
        )
        commit()  # Explicitly committing the changes
        logger.info(f"Event added for instance_id={instance_id}")
        return {"status": "success"}
    except Exception as e:
        rollback()  # Reverting any changes due to the error
        logger.error(f"Error adding event for instance_id={instance_id}: {e}")
        return {"status": "error", "message": str(e)}


@db_session
def get_all_events():
    logger.info("Fetching all events")
    return select(e for e in Event)[:]


@db_session
def add_running_instance(instance_id):
    try:
        RunningInstance(instance_id=instance_id, running=True)
        commit()
        logger.info(f"Running instance added with instance_id={instance_id}")
        return {"status": "success"}
    except Exception as e:
        rollback()
        logger.error(
            f"Error adding running instance with instance_id={instance_id}: {e}"
        )
        return {"status": "error", "message": str(e)}


@db_session
def finish_running_instance(instance):
    try:
        finished_instance = RunningInstance.get(instance_id=instance)
        if finished_instance:
            finished_instance.running = False
            commit()
            logger.info(f"Running instance finished with instance_id={instance}")
            return {"status": "success"}
        else:
            logger.warning(f"Instance not found with instance_id={instance}")
            return {"status": "error", "message": "Instance not found"}
    except Exception as e:
        rollback()
        logger.error(f"Error finishing instance with instance_id={instance}: {e}")
        return {"status": "error", "message": str(e)}


@db_session
def delete_instance(instance_id):
    try:
        instance_to_delete = RunningInstance.get(instance_id=instance_id)
        if instance_to_delete:
            instance_to_delete.delete()
            commit()
            logger.info(f"Instance deleted with instance_id={instance_id}")
            return {"status": "success"}
        else:
            logger.warning(
                f"Instance not found for deletion with instance_id={instance_id}"
            )
            return {"status": "error", "message": "Instance not found"}
    except Exception as e:
        rollback()
        logger.error(f"Error deleting instance with instance_id={instance_id}: {e}")
        return {"status": "error", "message": str(e)}


@db_session
def get_running_instances_log():
    try:
        log = []
        logger.info("Fetching running instances log")
        running_instances = RunningInstance.select()[:]
        for instance in running_instances:
            instance_dict = {}
            instance_dict[instance.instance_id] = {}
            events = Event.select(
                lambda e: e.instance_id == instance.instance_id
            ).order_by(Event.timestamp)[:]
            events_list = []
            for event in events:
                model_path = event.model_name
                event_dict = {
                    "activity_id": event.activity_id,
                    "pending": event.pending,
                    "activity_variables": event.activity_variables,
                }
                events_list.append(event_dict)

            instance_dict[instance.instance_id]["model_path"] = model_path
            instance_dict[instance.instance_id]["events"] = events_list
            log.append(instance_dict)
        logger.info("Running instances log fetched")
        return log
    except Exception as e:
        logger.error(f"Error fetching running instances log: {e}")
        return {"status": "error", "message": str(e)}
