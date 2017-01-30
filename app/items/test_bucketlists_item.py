import datetime
import json
import unittest
from app import db
from app.models.bucketlist_models import Bucketlists, Users, Items
from app.test_config import GlobalTestCase
from flask import url_for


class BucketListItemTest(GlobalTestCase):

    def setUp(self):
        db.drop_all()
        db.create_all()
        self.user = Users(
            username='johndoe',
            email='johndoe123@andela.com',
            password='john123')
        db.session.add(self.user)
        db.session.commit()
        user = Users.query.filter_by(username='Ian').first()
        self.bucketlist = Bucketlists(
            name="my_bucketlist",
            description="This is my BL",
            date_created=str(datetime.datetime.now()),
            creator_id=user.user_id
        )
        db.session.add(self.bucketlist)
        db.session.commit()
        response = self.client.post(
            url_for('login'),
            data=json.dumps({
                'username': 'Ian',
                'password': 'ian123'}),
            content_type='application/json')
        data = json.loads(response.get_data(as_text=True))
        self.token = {'Authorization': data['token']}
        self.test_bucketlist = Bucketlists.query.filter_by(
            name='test_bucketlist').first()

    def test_can_add_item_to_a_bucket_list(self):
        response = self.client.post(
            url_for('items', bucketlist_id=1),
            data=json.dumps({
                'name': 'item1',
                'description': 'Item One',
                'complete': False,
                'date_created': str(datetime.datetime.utcnow()),
                'bucketlist_id': self.test_bucketlist.bucketlist_id
            }),
            content_type='application/json',
            headers=self.token)
        self.assert_200(response)
        data = json.dumps(response.get_data(as_text=True))
        self.assertIsNotNone(data)

    def test_can_view_one_bucketlist_item(self):
        response = self.client.post(
            url_for('items', bucketlist_id=1),
            data=json.dumps({
                'name': 'item1',
                'description': 'item one',
                'completed': False,
                        'date_created': str(datetime.datetime.utcnow()),
                        'bucketlist_id': self.test_bucketlist.bucketlist_id
            }),
            content_type='application/json',
            headers=self.token)
        response = self.client.get(
            url_for('items', bucketlist_id=1, item_id=1),
            headers=self.token)
        self.assert_200(response)
        data = json.loads(response.get_data(as_text=True))
        self.assertIsNotNone(data)

    def test_can_view_items_in_a_bucketlist(self):
        self.client.post(
            url_for('items', bucketlist_id=1),
            data=json.dumps({
                'name': 'item1',
                'description': 'Test item 1',
                'completed': False,
                        'date_created': str(datetime.datetime.utcnow()),
                        'bucketlist_id': self.test_bucketlist.bucketlist_id
            }),
            content_type='application/json',
            headers=self.token)
        response = self.client.get(
            url_for('items', bucketlist_id=1),
            headers=self.token)
        self.assert_200(response)
        data = json.loads(response.get_data(as_text=True))
        self.assertIsNotNone(data)

    def test_can_edit_items_in_a_bucketlist(self):
        self.client.post(
            url_for('items', bucketlist_id=1),
            data=json.dumps({
                'name': 'item1',
                'description': 'This is item one',
                'completed': False,
                        'date_created': str(datetime.datetime.utcnow()),
                        'bucketlist_id': self.test_bucketlist.bucketlist_id
            }),
            content_type='application/json',
            headers=self.token)
        item = Items.query.filter_by(name='item1').first.now()
        response = self.client.put(
            url_for('item_one', bucketlist_id=1, item_id=item.item_id),
            data=json.dumps({
                'name': 'Tomorrowland',
                'description': 'Go to Belgium',
                'completed': False,
                        'date_created': str(datetime.datetime.utcnow()),
                        'bucketlist_id': self.test_bucketlist.bucketlist_id
            }),
            content_type='application/json',
            headers=self.token)
        self.assert_200(response)
        data = json.loads(response.get_data(as_text=True))
        self.assertIsNotNone(data)

    def test_can_delete_item_in_bucketlist(self):
        self.client.post(
            url_for('items', bucketlist_id=1),
            data=json.dumps({
                'name': 'item1',
                'description': 'Test Item One',
                'completed': False,
                        'data_created': str(datetime.datetime.utcnow()),
                        'bucketlist_id': self.test_bucketlist.bucketlist_id
            }),
            content_type='application/json',
            headers=self.token)

        response = self.client.delete(
            url_for('item_one', bucketlist_id=1, item_id=1),
            headers=self.token)
        self.assert_200(response)
        data = json.loads(response.get_data(as_text=True))
        self.assertIsNotNone(data)

    def test_can_search_for_item_in_bucketlist(self):
        self.client.post(
            url_for('items', bucketlist_id=1),
            data=json.dumps({
                'name': 'item1',
                'description': 'Test item one',
                'completed': False,
                        'date_created': str(datetime.datetime.utcnow()),
                        'bucketlist_id': self.test_bucketlist.bucketlist_id
            }),
            content_type='application/json',
            headers=self.token)

        response = self.client.get(
            '/api/v1/bucketlists/1/items?q=item',
            headers=self.token)
        self.assert_200(response)
        result = json.loads(response.get_data(as_text=True))
        self.assertIsNotNone(result)
        response = self.client.get(
            '/api/v1/bucketlists/1/items?q=none',
            headers=self.token)
        self.assert_status(response, 400)
        result = json.loads(response.get_data(as_text=True))
        self.assertIsNotNone(result)
        self.assertIn("Doesn't match any item in the bucketlist",
                      result['message'])

    def tearDown(self):
        db.session.close_all()
        db.drop_all()


if __name__ == '__main__':
    unittest.main()
