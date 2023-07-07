from enum import Enum
import enum
from enum import Enum, EnumMeta


class user_configs():
    """
    Defines settings defined in the config file.
    """
    def __init__(self, config):
        #read databases related config
        self.dbhost = config["database"]["host"]
        self.dbusername = config["database"]["username"]
        self.dbpassword = config["database"]["password"]
        self.dbname = config["database"]["db_name"]
        self.dbport = config["database"]["port"]

        #read dashboard related config
        self.grafana_url = config["dashboard"]["grafana_url"]
        self.dashboard_uid= config["dashboard"]["UID"]
        self.create_dashboard = config["dashboard"]["dashboard_creation"]["create"]
        self.base_dashboard_location = config["dashboard"]["dashboard_creation"]["dashboard_json_location"]
        self.dashboard_title = config["dashboard"]["dashboard_creation"]["title"]
        self.username = config["dashboard"]["username"]
        self.password = config["dashboard"]["password"]

class db_configs():
    """
    Defines settings defined in the config file.
    """
    def __init__(self, config):
        self.host = config["dashboard"]["grafana_url"]
        self.dashboard_uid= config["dashboard"]["UID"]
        self.create_dashboard = config["dashboard"]["dashboard_creation"]["create"]
        self.base_dashboard_location = config["dashboard"]["dashboard_creation"]["dashboard_json_location"]
        self.dashboard_title = config["dashboard"]["dashboard_creation"]["title"]
        self.username = config["dashboard"]["username"]
        self.password = config["dashboard"]["password"]


states = ["user1.Initial", 
"user1.ArriveFloorIN",
"user1.waiting",
"user1.elevator", 
"user1.elevator.Initial", 
"user1.elevator.callreceived",
"user1.elevator.decision",
"user1.elevator.decision.Initial",
"user1.elevator.goingup",
"user1.elevator.neutral",
"user1.getin",
"user1.elevator.goingdown", 
"user1.GoFloorOUT",
"user1.ExitSystem",
"user1.giveup",
"user1.final"]


states_calc = ["calculator.Initial",
            "calculator.on",
            "calculator.on.Initial",
            "calculator.on.operand1",
            "calculator.on.opEntered",
            "calculator.on.operand2",
            "calculator.on.result",
            "calculator.Final",
]