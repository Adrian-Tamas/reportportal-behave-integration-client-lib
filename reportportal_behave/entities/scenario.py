class Scenario:

    def __init__(self, scenario, feature_id=None, scenario_id=None):
        self.name = f"Scenario: {scenario.name}"
        self.description = scenario.name
        self.tags = scenario.tags
        self.item_type = "SCENARIO"
        self.feature_id = feature_id
        self.scenario_id = scenario_id
