class Feature:

    def __init__(self, feature, feature_id=None):
        self.name = feature.name
        self.description = f"Feature description:\n {feature.description} \n"
        self.tags = feature.tags
        self.item_type = "SUITE"
        self.feature_id = feature_id
