from app import app, db
from app.models import *
from flask.ext.migrate import MigrateCommand
from flask.ext.script import Manager, Command
from datetime import datetime
from seed import SeedCommand

manager = Manager(app)
manager.add_command('db', MigrateCommand)
manager.add_command('seed', SeedCommand)

if __name__ == '__main__':
    manager.run()