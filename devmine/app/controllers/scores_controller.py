import json

from sqlalchemy.orm.exc import NoResultFound

from devmine.app.models.score import Score
from devmine.app.controllers.application_controller import (
    ApplicationController
)
from devmine.app.helpers import application_helper as ah


class ScoresController(ApplicationController):

    def index(self, db):
        """Return the list of all scores."""
        since_id = super().get_since_id()
        try:
            scores = db.query(Score).filter(Score.id.between(
                since_id, since_id + 100)).all()
        except NoResultFound:
            scores = {}
        return json.dumps(scores, cls=ah.AlchemyEncoder)

    def show(self, db, id):
        """Return the repository corresponding to the given id."""
        try:
            score = db.query(Score).filter_by(id=id).one()
        except NoResultFound:
            score = {}
        return json.dumps(score, cls=ah.AlchemyEncoder)
