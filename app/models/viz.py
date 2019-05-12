from db import mongo

class VizUnstructureModel:

    def __init__(self, viz):
        self.viz = viz

    def save_viz_to_db(self):
        viz = self.viz
        return mongo.db.viz.insert_one(viz).inserted_id

    @classmethod
    def find_by_object_id(cls, id):
        return mongo.db.viz.find_one({'_id': id})
