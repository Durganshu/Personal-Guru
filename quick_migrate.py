import os
os.environ['SKIP_BACKGROUND_TASKS'] = 'True'
os.environ['TESTING'] = 'True'  # To skip even more init
from app import create_app, db  # noqa: E402
print("Starting rapid db.create_all()...")
app = create_app()
with app.app_context():
    db.create_all()
    print("db.create_all() success.")
