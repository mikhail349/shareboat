import datetime
import json
import time

from django.contrib.auth.models import Group
from django.test import tag, Client, TestCase
from django.urls import reverse

from base.models import Base
from boat.models import Boat, BoatFav, BoatFile, Manufacturer, Model, Tariff
from boat.tests.test_models import create_model, create_simple_boat
from booking.models import Booking
from chat.models import MessageBoat
from file.tests.test_models import get_imagefile
from user.tests.test_models import (create_boat_owner, create_moderator,
                                    create_user)


class TariffTestCase(TestCase):
    def setUp(self):
        self.user = create_user('user@mail.com', '12345')
        self.owner = create_boat_owner('owner@mail.com', '12345')
        self.model = create_model()
        self.boat = create_simple_boat(self.model, self.owner)
        self.client = Client()

    def test_create(self):
        # anon
        response = self.client.get(reverse('boat:create_tariff'))
        self.assertRedirects(response, expected_url=reverse(
            'user:login') + '?next=' + reverse('boat:create_tariff'))

        # some user
        self.client.login(email='user@mail.com', password='12345')
        response = self.client.get(reverse('boat:create_tariff'))
        self.assertEqual(response.status_code, 403)

        # owner
        self.client.login(email='owner@mail.com', password='12345')
        response = self.client.get(reverse('boat:create_tariff'), {
                                   'boat_pk': self.boat.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['form'].initial['boat'], str(self.boat.pk))

        # ok
        data = {
            'boat': self.boat.pk,
            'start_date': '2022-01-01',
            'end_date': '2022-01-31',
            'name': 'My Tariff',
            'duration': 1,
            'min': 1,
            'price': 10_000.32,
            'mon': True
        }
        response = self.client.post(reverse('boat:create_tariff'), data)
        self.assertRedirects(response, expected_url=reverse(
            'boat:view', kwargs={'pk': self.boat.pk}) + '#tariffs')

        # wrong model validation
        data['mon'] = False
        response = self.client.post(reverse('boat:create_tariff'), data)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.context['form'].errors)

        # wrong boat status
        data['mon'] = True
        self.boat.status = Boat.Status.DELETED
        self.boat.save()
        response = self.client.post(reverse('boat:create_tariff'), data)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.context['form'].errors)

        # wrong boat owner
        self.boat.status = Boat.Status.SAVED
        self.boat.owner = self.user
        self.boat.save()
        response = self.client.post(reverse('boat:create_tariff'), data)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.context['form'].errors)

    def test_update(self):
        tariff = Tariff.objects.create(boat=self.boat, active=True, start_date=datetime.date(2022, 1, 1), end_date=datetime.date(2022, 12, 31),
                                       name='My Second Tariff', duration=1, min=1, mon=True, tue=True, wed=True, thu=True, fri=True, sat=True, sun=True, price=500
                                       )
        reversed = reverse('boat:update_tariff', kwargs={'pk': tariff.pk})

        # anon
        self.client.logout()
        response = self.client.get(reversed)
        self.assertRedirects(response, expected_url=reverse(
            'user:login') + '?next=' + reversed)

        # some user
        self.client.login(email='user@mail.com', password='12345')
        response = self.client.get(reversed)
        self.assertEqual(response.status_code, 403)

        # owner

        # get
        self.client.login(email='owner@mail.com', password='12345')
        response = self.client.get(reversed)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['form'].instance.name, 'My Second Tariff')

        # not found
        response = self.client.get(
            reverse('boat:update_tariff', kwargs={'pk': 382}))
        self.assertEqual(response.status_code, 404)

        # post
        data = {
            'boat': self.boat.pk,
            'start_date': '2022-01-01',
            'end_date': '2022-01-31',
            'name': 'My Second Tariff',
            'duration': 1,
            'min': 1,
            'price': 10_000.32,
            'mon': True
        }
        # not found
        response = self.client.post(
            reverse('boat:update_tariff', kwargs={'pk': 382}), data)
        self.assertEqual(response.status_code, 404)

        # ok
        response = self.client.post(
            reverse('boat:update_tariff', kwargs={'pk': tariff.pk}), data)
        self.assertRedirects(response, expected_url=reverse(
            'boat:view', kwargs={'pk': self.boat.pk}) + '#tariffs')

        # wrong
        data['mon'] = False
        response = self.client.post(
            reverse('boat:update_tariff', kwargs={'pk': tariff.pk}), data)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.context['form'].errors)

    def test_delete(self):
        tariff = Tariff.objects.create(boat=self.boat, active=True, start_date=datetime.date(2022, 1, 1), end_date=datetime.date(2022, 12, 31),
                                       name='My Tariff To Be Deleted', duration=1, min=1, mon=True, tue=True, wed=True, thu=True, fri=True, sat=True, sun=True, price=500
                                       )
        reversed = reverse('boat:delete_tariff', kwargs={'pk': tariff.pk})

        # anon
        self.client.logout()
        response = self.client.post(reversed)
        self.assertRedirects(response, expected_url=reverse(
            'user:login') + '?next=' + reversed)

        # some user
        self.client.login(email='user@mail.com', password='12345')
        response = self.client.post(reversed)
        self.assertEqual(response.status_code, 403)

        # owner
        self.client.login(email='owner@mail.com', password='12345')
        response = self.client.post(reversed)
        self.assertRedirects(response, expected_url=reverse(
            'boat:view', kwargs={'pk': self.boat.pk}) + '#tariffs')

        # not found
        response = self.client.post(
            reverse('boat:delete_tariff', kwargs={'pk': 2342}))
        self.assertEqual(response.status_code, 404)


class BoatTestCase(TestCase):

    def _get_post_data(self):
        return {
            'name': 'Boat2',
            'length': 1,
            'width': 1,
            'draft': 1,
            'capacity': 1,
            'model': self.model.pk,
            'file': get_imagefile(),
            'type': Boat.Type.SAILING_YACHT,
            'motor_amount': 1,
            'motor_power': 8,
            'berth_amount': 2,
            'extra_berth_amount': 0,
            'cabin_amount': 1,
            'bathroom_amount': 3,

            'is_custom_location': True,
            'boat_coordinates': '{"lat": 123.456789, "lon": 987.654321, "address": "Russia, Moscow", "state": "Moscow"}'
        }

    def setUp(self):
        self.user = create_user('someuser@mail.ru', '12345')
        create_boat_owner('owner2@mail.ru', '12345')
        self.owner = create_boat_owner('owner@mail.ru', '12345')
        self.model = create_model()
        self.boat = create_simple_boat(self.model, self.owner)
        self.client = Client()

    def test_get_models(self):
        manufacturer = Manufacturer.objects.create(name="Manufacturer1")
        m1 = Model.objects.create(name="Model1", manufacturer=manufacturer)
        m2 = Model.objects.create(name="Model2", manufacturer=manufacturer)

        self.client.login(email='someuser@mail.ru', password='12345')
        response = self.client.get(
            reverse('boat:api_get_models', kwargs={'pk': manufacturer.pk}))
        self.assertDictEqual(json.loads(response.content), {
            'data': [
                {
                    'id': m1.pk,
                    'name': 'Model1'

                },
                {
                    'id': m2.pk,
                    'name': 'Model2'
                }
            ]
        })

    def test_my_boats(self):
        self.client.login(email='someuser@mail.ru', password='12345')
        response = self.client.get(reverse('boat:my_boats'))
        self.assertEqual(response.status_code, 403)

        self.client.login(email='owner@mail.ru', password='12345')
        response = self.client.get(reverse('boat:my_boats'))
        self.assertEqual(len(response.context['boats']), 1)

        self.client.login(email='owner2@mail.ru', password='12345')
        response = self.client.get(reverse('boat:my_boats'))
        self.assertEqual(len(response.context['boats']), 0)

    def test_set_status(self):
        self.client.login(email='owner2@mail.ru', password='12345')
        response = self.client.post(reverse('boat:api_set_status', kwargs={
                                    'pk': self.boat.pk}), {'status': Boat.Status.ON_MODERATION})
        self.assertEqual(response.status_code, 404)

        self.client.login(email='owner@mail.ru', password='12345')
        response = self.client.post(reverse('boat:api_set_status', kwargs={
                                    'pk': self.boat.pk}), {'status': Boat.Status.SAVED})
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(json.loads(response.content), {
                             'message': 'Некорректный статус'})

        response = self.client.post(reverse('boat:api_set_status', kwargs={
                                    'pk': self.boat.pk}), {'status': Boat.Status.ON_MODERATION})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Boat.objects.get(
            pk=self.boat.pk).status, Boat.Status.ON_MODERATION)

    def test_create_boat(self):
        self.client.login(email='owner@mail.ru', password='12345')

        response = self.client.get(reverse('boat:create'))
        self.assertEqual(response.status_code, 200)

        data = {
            'model': 982,
            'file': [get_imagefile() for _ in range(35)]
        }

        response = self.client.post(reverse('boat:create'), data)
        self.assertEqual(response.status_code, 400)
        msg = json.loads(response.content)['message']
        self.assertEqual(msg[0], 'Модель не найдена')
        self.assertEqual(msg[1], 'Можно приложить не более 30 фотографий')

        response = self.client.post(
            reverse('boat:create'), self._get_post_data())
        self.assertEqual(response.status_code, 200)

        boat_pk = json.loads(response.content)['data']['id']
        boat = Boat.objects.get(pk=boat_pk)
        self.assertTrue(hasattr(boat, 'motor_boat'))
        self.assertTrue(hasattr(boat, 'comfort_boat'))
        self.assertTrue(hasattr(boat, 'coordinates'))

    def test_update_boat(self):
        self.client.login(email='owner@mail.ru', password='12345')

        response = self.client.get(reverse('boat:update', kwargs={'pk': 997}))
        self.assertEqual(response.status_code, 404)

        response = self.client.get(
            reverse('boat:update', kwargs={'pk': self.boat.pk}))
        self.assertEqual(response.status_code, 200)

        self.boat.status = Boat.Status.DECLINED
        self.boat.save()
        response = self.client.post(
            reverse('boat:update', kwargs={'pk': self.boat.pk}), self._get_post_data())
        self.boat = Boat.objects.get(pk=self.boat.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.boat.status, Boat.Status.SAVED)

        self.boat.status = Boat.Status.PUBLISHED
        self.boat.save()
        response = self.client.post(
            reverse('boat:update', kwargs={'pk': self.boat.pk}), self._get_post_data())
        self.boat = Boat.objects.get(pk=self.boat.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.boat.status, Boat.Status.ON_MODERATION)

        data = {
            **self._get_post_data(),
            'type': Boat.Type.BOAT,
            'is_custom_location': False
        }
        response = self.client.post(
            reverse('boat:update', kwargs={'pk': self.boat.pk}), data)
        self.boat = Boat.objects.get(pk=self.boat.pk)
        self.assertFalse(hasattr(self.boat, 'motor_boat'))
        self.assertFalse(hasattr(self.boat, 'comfort_boat'))
        self.assertFalse(hasattr(self.boat, 'coordinates'))

        response = self.client.post(
            reverse('boat:update', kwargs={'pk': 956}), self._get_post_data())
        self.assertTrue(response.status_code, 404)

    def test_favs(self):

        Boat.objects.create(name='Boat1', length=1, width=1, draft=1, capacity=1, model=self.model,
                            type=Boat.Type.BOAT, owner=self.owner, status=Boat.Status.PUBLISHED)
        boat2 = Boat.objects.create(name='Boat2', length=1, width=1, draft=1, capacity=1,
                                    model=self.model, type=Boat.Type.BOAT, owner=self.owner, status=Boat.Status.PUBLISHED)
        BoatFav.objects.create(boat=boat2, user=self.user)

        self.client.login(email='someuser@mail.ru', password='12345')
        response = self.client.get(reverse('boat:favs'))
        self.assertEqual(response.status_code, 200)

        boats = response.context['boats']
        self.assertTrue(len(boats) == 1 and boats[0].pk == boat2.pk)

    def test_boats_on_moderation(self):
        boat = create_simple_boat(self.model, self.owner)
        moderator = create_user('moderator@mail.com', '12345')
        self.client.login(email='moderator@mail.com', password='12345')

        response = self.client.get(reverse('boat:boats_on_moderation'))
        self.assertEqual(response.status_code, 403)

        moderator.groups.add(Group.objects.get(name='boat_moderator'))
        response = self.client.get(reverse('boat:boats_on_moderation'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['boats']), 0)

        boat.status = Boat.Status.ON_MODERATION
        boat.save()
        response = self.client.get(reverse('boat:boats_on_moderation'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['boats']), 1)

    def test_moderate(self):
        boat = Boat.objects.create(name='Boat1', length=1, width=1, draft=1, capacity=1, model=self.model,
                                   type=Boat.Type.BOAT, owner=self.owner, status=Boat.Status.ON_MODERATION)
        moderator = create_user('moderator@mail.com', '12345')

        self.client.login(email='moderator@mail.com', password='12345')
        response = self.client.get(
            reverse('boat:moderate', kwargs={'pk': boat.pk}))
        self.assertEqual(response.status_code, 403)

        moderator.groups.add(Group.objects.get(name='boat_moderator'))

        response = self.client.get(
            reverse('boat:moderate', kwargs={'pk': boat.pk}))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse('boat:moderate', kwargs={'pk': 986}))
        self.assertEqual(response.status_code, 404)

    def test_delete(self):
        now = datetime.datetime.now()
        user = create_user('user@mail.com', '12345')
        boat = create_simple_boat(self.model, self.owner)
        booking = Booking.objects.create(
            boat=boat,
            renter=user,
            status=Booking.Status.ACCEPTED,
            start_date=datetime.date(now.year, 1, 1),
            end_date=datetime.date(now.year, 1, 10),
            total_sum=100.50,
            spec={"test": "123"}
        )
        self.client.login(email='user@mail.com', password='12345')

        response = self.client.post(
            reverse('boat:api_delete', kwargs={'pk': boat.pk}))
        self.assertEqual(response.status_code, 403)

        user.groups.add(Group.objects.get(name='boat_owner'))

        response = self.client.post(
            reverse('boat:api_delete', kwargs={'pk': boat.pk}))
        self.assertEqual(response.status_code, 404)

        self.client.login(email='owner@mail.ru', password='12345')
        response = self.client.post(
            reverse('boat:api_delete', kwargs={'pk': boat.pk}))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content)
                         ['code'], 'invalid_status')

        booking.status = Booking.Status.DONE
        booking.save()
        response = self.client.post(
            reverse('boat:api_delete', kwargs={'pk': boat.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Boat.objects.get(
            pk=boat.pk).status, Boat.Status.DELETED)

    def test_get_files(self):
        def _get_response():
            return self.client.get(reverse('boat:api_get_files', kwargs={'pk': self.boat.pk}))

        BoatFile.objects.create(boat=self.boat, file=get_imagefile())
        BoatFile.objects.create(boat=self.boat, file=get_imagefile())

        # anon
        self.client.logout()
        response = _get_response()
        self.assertEqual(response.status_code, 302)

        # wrong user
        self.client.login(email='someuser@mail.ru', password='12345')
        response = _get_response()
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)['data']
        self.assertListEqual(data, [])

        # owner
        self.client.login(email='owner@mail.ru', password='12345')
        response = _get_response()
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)['data']
        self.assertEqual(len(data), 2)

    def test_accept(self):
        def _get_response():
            return self.client.post(reverse('boat:accept', kwargs={'pk': self.boat.pk}), {'modified': self.boat.modified})

        # no access
        self.client.login(email='someuser@mail.ru', password='12345')
        response = _get_response()
        self.assertEqual(response.status_code, 403)

        create_moderator('moderator@mail.ru', '12345')
        self.client.login(email='moderator@mail.ru', password='12345')

        # wrong status
        self.boat.status = Boat.Status.SAVED
        self.boat.save()
        response = _get_response()
        self.assertEqual(response.status_code, 404)

        # ok
        self.boat.status = Boat.Status.ON_MODERATION
        self.boat.save()
        response = _get_response()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Boat.objects.get(
            pk=self.boat.pk).status, Boat.Status.PUBLISHED)

        # wrong timestamp
        old_boat_modified = self.boat.modified
        self.boat.status = Boat.Status.ON_MODERATION
        self.boat.save()
        response = self.client.post(reverse('boat:accept', kwargs={'pk': self.boat.pk}), {
                                    'modified': old_boat_modified})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.context.get('errors'),
                         'Лодка была изменена. Выполните проверку еще раз.')

    def test_reject(self):
        def _get_response():
            return self.client.post(reverse('boat:reject', kwargs={'pk': self.boat.pk}), {'modified': self.boat.modified, 'comment': 'Плохая лодка'})

        # no access
        self.client.login(email='someuser@mail.ru', password='12345')
        response = _get_response()
        self.assertEqual(response.status_code, 403)

        create_moderator('moderator@mail.ru', '12345')
        self.client.login(email='moderator@mail.ru', password='12345')

        # wrong status
        self.boat.status = Boat.Status.SAVED
        self.boat.save()
        response = _get_response()
        self.assertEqual(response.status_code, 404)

        # ok
        self.boat.status = Boat.Status.ON_MODERATION
        self.boat.save()
        response = _get_response()
        message_boat = MessageBoat.objects.get(boat=self.boat)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Boat.objects.get(
            pk=self.boat.pk).status, Boat.Status.DECLINED)
        self.assertTrue(
            message_boat.sender == None and
            message_boat.recipient == self.boat.owner and
            message_boat.text == '<div>Лодка не прошла модерацию.</div><div>Объявление не соответствует правилам сервиса: Плохая лодка</div>'
        )

        # wrong timestamp
        old_boat_modified = self.boat.modified
        self.boat.status = Boat.Status.ON_MODERATION
        self.boat.save()
        response = self.client.post(reverse('boat:reject', kwargs={'pk': self.boat.pk}), {
                                    'modified': old_boat_modified})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.context.get('errors'),
                         'Лодка была изменена. Возможно, недочёты исправлены.')

    def test_search_boats(self):
        def _get_response(params):
            return self.client.get(reverse('boat:search_boats'), params)

        def _create_published_boat():
            base = Base.objects.create(
                name='Base1', lon=123.456789, lat=987.654321, address="Moscow, 15", state="Moscow")
            return Boat.objects.create(
                name='Boat1',
                length=1, width=1, draft=1, capacity=1,
                model=self.model,
                type=Boat.Type.BOAT,
                owner=self.owner,
                status=Boat.Status.PUBLISHED,
                base=base
            )

        now = datetime.datetime.now()
        target_year = now.year + 1
        boat = _create_published_boat()
        Tariff.objects.create(boat=boat, active=True, start_date=datetime.date(target_year, 1, 1), end_date=datetime.date(target_year, 1, 10),
                              name='Суточно', duration=1, min=1,
                              mon=True, tue=True, wed=True, thu=True, fri=True, sat=True, sun=True, price=500
                              )
        Tariff.objects.create(boat=boat, active=True, start_date=datetime.date(target_year, 1, 1), end_date=datetime.date(target_year, 1, 10),
                              name='Неделя', duration=7, min=1,
                              mon=True, tue=True, wed=True, thu=True, fri=True, sat=True, sun=True, price=8_000
                              )

        response = _get_response({
            'dateFrom': '%s-01-03' % target_year,
            'dateTo': '%s-01-05' % target_year,
            'state': 'Moscow',
            'boatType': [Boat.Type.BOAT]
        })
        self.assertEqual(response.status_code, 200)
        boats = response.context.get('boats', [])
        self.assertEqual(len(boats), 1)
        self.assertEqual(boats[0].actual_tariffs[0].price_per_day, 500)

        response = _get_response({})
        self.assertEqual(response.status_code, 200)
        boats = response.context.get('boats', [])
        self.assertEqual(len(boats), 1)
        self.assertEqual(boats[0].actual_tariffs[0].price_per_day, 500)

        # wrong state
        response = _get_response({
            'dateFrom': '%s-01-03' % target_year,
            'dateTo': '%s-01-05' % target_year,
            'state': 'SPB'
        })
        self.assertEqual(response.status_code, 200)
        boats = response.context.get('boats', [])
        self.assertEqual(len(boats), 0)

    @tag('slow')
    def test_search_boats_time(self):
        now = datetime.datetime.now()
        for i in range(1000):
            boat = Boat.objects.create(name=f'Boat{i}', length=1, width=1, draft=1, capacity=1,
                                       model=self.model, type=Boat.Type.BOAT, owner=self.owner, status=Boat.Status.PUBLISHED)
            Tariff.objects.create(boat=boat, active=True, start_date=datetime.date(now.year, 1, 1), end_date=datetime.date(now.year, 12, 31),
                                  name='Суточно', duration=1, min=1, price=500,
                                  mon=True, tue=True, wed=True, thu=True, fri=True, sat=True, sun=True,
                                  )
            Tariff.objects.create(boat=boat, active=True, start_date=datetime.date(now.year, 1, 1), end_date=datetime.date(now.year, 12, 31),
                                  name='Неделя', duration=7, min=1, price=8_000,
                                  thu=True,
                                  )
            Tariff.objects.create(boat=boat, active=True, start_date=datetime.date(now.year, 1, 1), end_date=datetime.date(now.year, 12, 31),
                                  name='Выходные', duration=3, min=1, price=2_000,
                                  fri=True,
                                  )

        start_time = time.time()
        response = self.client.get(reverse('boat:search_boats'), {
                                   'dateFrom': '%s-01-03' % now.year, 'dateTo': '%s-01-17' % now.year})
        exec_time = time.time() - start_time
        self.assertLess(exec_time, 2.0)
        self.assertEqual(response.status_code, 200)

    def test_switch_fav(self):
        def _get_response(pk):
            return self.client.get(reverse('boat:api_switch_fav', kwargs={'pk': pk}))

        # anon
        response = _get_response(self.boat.pk)
        self.assertEqual(response.status_code, 302)

        # login
        self.client.login(email='someuser@mail.ru', password='12345')

        # not found
        response = _get_response(758)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)['data']
        self.assertIsNone(data)

        # added
        response = _get_response(self.boat.pk)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)['data']
        self.assertEqual(data, 'added')
        self.assertTrue(BoatFav.objects.filter(
            boat=self.boat, user=self.user).exists())

        # deleted
        response = _get_response(self.boat.pk)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)['data']
        self.assertEqual(data, 'deleted')
        self.assertFalse(BoatFav.objects.filter(
            boat=self.boat, user=self.user).exists())

    def test_booking(self):
        def _get_response(pk):
            return self.client.get(reverse('boat:booking', kwargs={'pk': pk}))

        response = _get_response(989)
        self.assertEqual(response.status_code, 404)

        now = datetime.datetime.now()
        boat = Boat.objects.create(name='Boat1', length=1, width=1, draft=1, capacity=1,
                                   model=self.model, type=Boat.Type.BOAT, owner=self.owner, status=Boat.Status.PUBLISHED)

        Tariff.objects.create(boat=boat, active=True, start_date=datetime.date(now.year, 1, 1), end_date=datetime.date(now.year, 1, 30),
                              name='Суточно', duration=1, min=1, price=500,
                              mon=True, tue=True, wed=True, thu=True, fri=True, sat=True, sun=True,
                              )
        Tariff.objects.create(boat=boat, active=True, start_date=datetime.date(now.year+1, 1, 1), end_date=datetime.date(now.year+1, 1, 30),
                              name='Суточно', duration=1, min=1, price=2_000,
                              mon=True, tue=True, wed=True, thu=True, fri=True, sat=True, sun=True,
                              )

        Booking.objects.create(boat=boat, renter=self.user, status=Booking.Status.ACCEPTED,
                               start_date=datetime.date(now.year, 1, 3),
                               end_date=datetime.date(now.year, 1, 6),
                               total_sum=1_500,
                               spec={"test": "123"}
                               )

        response = _get_response(boat.pk)
        self.assertEqual(response.status_code, 200)

        context = response.context
        self.assertEqual(context['boat'], boat)
        self.assertEqual(context['first_price_date'],
                         datetime.date(now.year, 1, 1))
        self.assertEqual(context['last_price_date'],
                         datetime.date(now.year+1, 1, 30))
        self.assertTrue(context['prices_exist'])
        self.assertListEqual(context['price_ranges'], [
            [datetime.date(now.year, 1, 1), datetime.date(now.year, 1, 30)],
            [datetime.date(now.year+1, 1, 1),
             datetime.date(now.year+1, 1, 30)],
        ])
        self.assertListEqual(context['accepted_bookings_ranges'], [
            [datetime.date(now.year, 1, 3), datetime.date(now.year, 1, 6)],
        ])

    def test_calc_booking(self):
        now = datetime.datetime.now()
        boat = Boat.objects.create(name='Boat1', length=1, width=1, draft=1, capacity=1,
                                   model=self.model, type=Boat.Type.BOAT, owner=self.owner, status=Boat.Status.PUBLISHED)
        tariff = Tariff.objects.create(boat=boat, active=True, start_date=datetime.date(now.year, 1, 1), end_date=datetime.date(now.year, 1, 10),
                                       name='Суточно', duration=1, min=1, price=500,
                                       mon=True, tue=True, wed=True, thu=True, fri=True, sat=True, sun=True,
                                       )

        # wrong period
        response = self.client.get(
            reverse('boat:api_calc_booking', kwargs={'pk': boat.pk}),
            {
                'start_date': datetime.date(now.year, 1, 1),
                'end_date': datetime.date(now.year, 1, 25)
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(json.loads(response.content), {})

        # ok
        response = self.client.get(
            reverse('boat:api_calc_booking', kwargs={'pk': boat.pk}),
            {
                'start_date': datetime.date(now.year, 1, 3),
                'end_date': datetime.date(now.year, 1, 5)
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(json.loads(response.content), {
            'sum': "1000.00",
            'days': 2,
            'spec': {
                str(tariff.pk): {
                    'name': 'Суточно',
                    'price': '500.00',
                    'amount': 2,
                    'sum': '1000.00'
                }
            }
        })

    def test_view(self):
        boat = Boat.objects.create(name='Boat1', length=1, width=1, draft=1, capacity=1,
                                   model=self.model, type=Boat.Type.BOAT, owner=self.owner, status=Boat.Status.PUBLISHED)

        # anon
        response = self.client.get(
            reverse('boat:view', kwargs={'pk': boat.pk}))
        self.assertEqual(response.status_code, 302)

        # foreign boat
        self.client.login(email='someuser@mail.ru', password='12345')
        response = self.client.get(
            reverse('boat:view', kwargs={'pk': boat.pk}))
        self.assertEqual(response.status_code, 404)

        # ok
        self.client.login(email='owner@mail.ru', password='12345')
        response = self.client.get(
            reverse('boat:view', kwargs={'pk': boat.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['boat'], boat)
