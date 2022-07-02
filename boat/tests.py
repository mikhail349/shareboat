from django.test import TestCase, Client
from django.urls import reverse
from boat.models import Boat
from user.tests import create_boat_owner

def create_simple_boat( owner):
    return Boat.objects.create(name='Лодка1', length=1, width=1, draft=1, capacity=1, type=Boat.Type.BOAT, owner=owner)      

class BoatTest(TestCase):

    # Функция для разовых настроек перед тестом
    def setUp(self):

        # Создаем "какого-то пользователя"      
        self.some_user = create_boat_owner('some_user@gmail.com', 'some_user_password')
        # Создаем лодку для "какого-то пользователя" 
        self.some_user_boat = create_simple_boat(self.some_user)

        # Создаем меня   
        me = create_boat_owner('me@gmail.com', 'my_password')
        # Создаем лодку для меня
        self.my_boat = create_simple_boat(me)

        # Модуль имитации пользователя при выполнении запросов
        self.client = Client() 
        # Логинюсь в качестве себя
        self.client.login(email='me@gmail.com', password="my_password")
   
    # Функция теста удаления чужой лодки
    def test_delete_foreign_boat(self):
        # POST-запрос с попыткой удалить лодку "какого-то пользователя"
        response = self.client.post(reverse('boat:api_delete', kwargs={'pk': self.some_user_boat.pk}))
        # Код статуса должен быть равен 404 (лодка не найдена)
        self.assertEqual(response.status_code, 404)

    # Функция теста удаления своей лодки
    def test_delete_my_boat(self): 
        # POST-запрос с попыткой удалить мою лодку 
        response = self.client.post(reverse('boat:api_delete', kwargs={'pk': self.my_boat.pk}))
        # Код статуса должен быть равен 200 (успешно)
        self.assertEqual(response.status_code, 200)