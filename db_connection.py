import records
import self


class Resources:
    def __init__(self, db_resource_url):
        self.db_url = db_resource_url

    def resource_value_retrieval(self):
        db = records.Database(self.db_url)
        rows = db.query("SELECT variable, value FROM resource_config;").all()
        map_resource_config_values = {row["variable"]:row["value"] for row in rows}
        return map_resource_config_values


