import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.workspace_service import add_watchlist_entity, create_workspace, get_or_create_user, list_watchlist


class WorkspaceServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        engine = create_engine("sqlite:///:memory:", future=True)
        Base.metadata.create_all(bind=engine)
        self.Session = sessionmaker(bind=engine, future=True)

    def test_create_workspace_and_watchlist(self) -> None:
        with self.Session() as db:
            user = get_or_create_user(db, "owner@example.com")
            workspace = create_workspace(db, user=user, name="Research")
            row = add_watchlist_entity(
                db,
                workspace_id=workspace.id,
                user_id=user.id,
                chain="btc",
                entity_type="address",
                entity_value="bc1test",
                label="Test address",
            )
            items = list_watchlist(db, workspace_id=workspace.id)

        self.assertEqual(workspace.name, "Research")
        self.assertEqual(row.entity_value, "bc1test")
        self.assertEqual(len(items), 1)


if __name__ == "__main__":
    unittest.main()
