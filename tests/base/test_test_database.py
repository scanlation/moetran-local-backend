from app.models.user import Team, User
from tests import MoeTestCase


class TestDatabaseTestCase(MoeTestCase):
    def test_is_clear1(self):
        """测试测试的每个新方法都会调用setUp清库"""
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(Team.objects.count(), 0)
