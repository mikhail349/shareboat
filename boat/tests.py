from django.test import TestCase, Client
from django.urls import reverse
from user.models import User
from boat.models import Boat

class BoatTest(TestCase):

    # Вспомогательная функция для создания обычной лодки
    def create_simple_boat(self, owner):
        return Boat.objects.create(name='Лодка1', length=1, width=1, draft=1, capacity=1, type=Boat.Type.BOAT, owner=owner)        

    # Функция для разовых настроек перед тестом
    def setUp(self):

        # Создаем "какого-то пользователя"      
        self.some_user = User.objects.create(email='some_user@gmail.com')
        self.some_user.set_password('some_user_password')
        self.some_user.save()
        # Создаем лодку для "какого-то пользователя" 
        self.some_user_boat = self.create_simple_boat(self.some_user)

        # Создаем меня   
        me = User.objects.create(email='me@gmail.com')
        me.set_password('my_password')
        me.save()
        # Создаем лодку для меня
        self.my_boat = self.create_simple_boat(me)

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

    # Функция теста получения только своих лодок
    def test_view_only_my_boats(self):
        response = self.client.get(reverse('boat:my_boats'))
        boats = response.context['boats']
        self.assertQuerysetEqual(boats.filter(owner=self.some_user), [])