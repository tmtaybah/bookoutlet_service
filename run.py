import os, sys
from bookoutlet_service import app, db
from bookoutlet_service.models import User, BookoutletBook, GoodreadsBook

THREADS_PER_PAGE = 2  # WHAT IS THIS ACTUALLY DOING?!!

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED = True

# clear data base tables without dropping them
def clear_data(session):
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print(f"Clear table: {table}")
        session.execute(table.delete())
    session.commit()


@app.shell_context_processor
def make_shell_context():
    return {
        "db": db,
        "User": User,
        "bookoutlet": BookoutletBook,
        "goodreads": GoodreadsBook,
    }


if __name__ == "__main__":

    db_path = "bookoutlet_service/site.db"
    if not os.path.isfile(db_path):
        print(f"Did not find db. Creating now...")
        db.create_all()

    if len(sys.argv) > 1 and sys.argv[1] == "cleardb":
        clear_data(db.session)

    app.run(debug=True)
