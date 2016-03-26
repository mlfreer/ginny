from app import db, cache
from sqlalchemy_utils.types.choice import ChoiceType


class Stage(db.Model):
    TYPES = [('input', 'Input'), ('options', 'Option')]

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), info={'label': 'Name'})
    display_name = db.Column(db.String(128), info={'label': 'Display name'})
    clazz = db.Column(ChoiceType(TYPES,impl=db.String(length=16)),
                      info={'label': 'Class'})
    options = db.Column(db.String(1024), info={'label': 'Variants for Option Stage'})
    description = db.Column(db.String(1024), info={'label': 'Description'})

    @classmethod
    @cache.memoize(timeout=3600)
    def get_stage(self, id):
        return Stage.query.filter(Stage.id == id).one()

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name