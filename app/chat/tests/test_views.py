import json
import time

from django.test import Client, TestCase
from django.urls import reverse

from boat.tests.test_models import (create_boat_owner, create_model,
                                    create_simple_boat)
from chat.models import MessageBoat, MessageSupport
from user.tests.test_models import create_user


class ChatTestCase(TestCase):

    def test_list_time(self):
        BOAT_AMOUNT = 100
        MSG_AMOUNT_PER_BOAT = 50

        owner = create_boat_owner('owner@gmail.com', '12345')
        model = create_model()

        for _ in range(BOAT_AMOUNT):
            boat = create_simple_boat(model, owner)
            
            for i in range(MSG_AMOUNT_PER_BOAT):
                MessageBoat.objects.create(boat=boat, text=f'Test Text {i}', recipient=boat.owner)

        client = Client()
        client.login(email='owner@gmail.com', password='12345')
        
        start_time = time.time()
        response = client.get(reverse('chat:list'))
        exec_time = time.time() - start_time

        self.assertLess(exec_time, 2.0)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['messages']), BOAT_AMOUNT + 1) # + support chat

    def test_message_time(self):
        MSG_AMOUNT = 1000

        user = create_user('user@gmail.com', '12345')

        for i in range(MSG_AMOUNT):
            MessageSupport.objects.create(text=f'Test Text {i}', recipient=user)

        client = Client()
        client.login(email='user@gmail.com', password='12345')
        
        start_time = time.time()
        response = client.get(reverse('chat:message'))
        exec_time = time.time() - start_time

        self.assertLess(exec_time, 2.0)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.context['messages'])), MSG_AMOUNT)
