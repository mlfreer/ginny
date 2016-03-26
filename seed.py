from flask.ext.script import Manager, Command
from app import app, db
from app.models import *
from datetime import datetime

class SeedCommand(Command):
    def run(self):
        session_id_length = Option(name='session_id_length', value='8')
        db.session.add(session_id_length)
        db.session.commit()

        admin_role = Role(name='admin')
        manager_role = Role(name='manager')
        pasha = User(email='ppodolsky@me.com',
                     password='$2a$10$G.CCpc0u9Y9hPtrDApnhHOcWLICLMpI/oQWgleeX8D7/EFQrhO4hK',
                     active=True)
        misha = User(email='1991f@mail.ru',
                     password='$2a$10$7Z2J/fofU3iZMUC2S5aCn.I5RM0MmdJCIwtbzJ.Y9gZK.QdWl4Cne',
                     active=True)
        pasha.roles.extend([admin_role, manager_role])
        misha.roles.extend([admin_role, manager_role])
        default_game = Game(title='Bargainer Game')
        stage1 = Stage(name='prediction',
                       display_name='Prediction Stage',
                       clazz='input',
                       description='How many group members (including yourself) do you think would choose Action Y?',
                       together=True)
        stage2 = Stage(name='action',
                       display_name='Action Stage',
                       clazz='options',
                       options='Action X;Action Y',
                       description='Choose an Action',
                       together=True)
        game_to_stage1 = GameToStage(game=default_game, stage=stage1, order_number=1)
        game_to_stage2 = GameToStage(game=default_game, stage=stage2, order_number=2)


        scheduled_date = datetime.today().utcnow()
        default_trial = GameTrial(game=default_game,
                            start_time=scheduled_date,
                            size_of_room=10)
        default_game.game_trials.append(default_trial)

        db.session.add(pasha)
        db.session.add(misha)
        db.session.add(default_game)
        db.session.add(stage1)
        db.session.add(stage2)
        db.session.add(game_to_stage1)
        db.session.add(game_to_stage2)
        db.session.commit()