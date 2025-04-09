from app.db.database import SessionLocal


class DBSession:

    @staticmethod
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
