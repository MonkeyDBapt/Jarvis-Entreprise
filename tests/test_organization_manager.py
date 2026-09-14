import unittest

from jarvis.core import Organization, OrganizationManager, Pole, Team


class OrganizationManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.organization = Organization("org", "JARVIS Enterprise")
        self.manager = OrganizationManager(self.organization)

    def test_add_and_get_pole(self) -> None:
        pole = Pole("pole", "Engineering")
        self.manager.add_pole(pole)

        self.assertIs(self.manager.get_pole("pole"), pole)
        self.assertEqual(self.organization.poles, [pole])

    def test_duplicate_pole_is_rejected(self) -> None:
        self.manager.add_pole(Pole("pole", "Engineering"))

        with self.assertRaises(ValueError):
            self.manager.add_pole(Pole("pole", "Other"))

    def test_add_get_and_remove_team(self) -> None:
        self.manager.add_pole(Pole("pole", "Engineering"))
        team = Team("team", "Platform")
        self.manager.add_team("pole", team)

        self.assertIs(self.manager.get_team("pole", "team"), team)
        self.assertIs(self.manager.remove_team("pole", "team"), team)
        self.assertEqual(self.manager.get_pole("pole").teams, [])

    def test_duplicate_team_is_rejected(self) -> None:
        self.manager.add_pole(Pole("pole", "Engineering"))
        self.manager.add_team("pole", Team("team", "Platform"))

        with self.assertRaises(ValueError):
            self.manager.add_team("pole", Team("team", "Other"))

    def test_unknown_pole_or_team_raises_key_error(self) -> None:
        with self.assertRaises(KeyError):
            self.manager.get_pole("missing")

        self.manager.add_pole(Pole("pole", "Engineering"))
        with self.assertRaises(KeyError):
            self.manager.get_team("pole", "missing")

    def test_remove_pole_returns_existing_pole(self) -> None:
        pole = Pole("pole", "Engineering")
        self.manager.add_pole(pole)

        self.assertIs(self.manager.remove_pole("pole"), pole)
        self.assertEqual(self.organization.poles, [])


if __name__ == "__main__":
    unittest.main()
