class Step:

    def __init__(self, step, scenario_id=None, step_id=None):
        self.name = step.name
        self.keyword = step.keyword
        self.item_type = "STEP"
        self.scenario_id = scenario_id
        self.step_id = step_id
        if step.table:
            table_data = []
            for row in step.table.rows:
                table_data.append('|'.join(row))
            self.description = "|%s|" % '|\n|'.join(table_data)
        elif step.text:
            # Logs step with text if it was provided
            self.description = step.text
        else:
            self.description = f"{self.keyword} {self.name}"
