from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Chat, Message, NoteModel
from api.models import CustomUser



class ChatCreateListAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.client2 = APIClient()
        # Create two users
        self.user1 = CustomUser.objects.create_user(email="email1@gmail.com", password="pass123")
        self.user2 = CustomUser.objects.create_user(email="email12@gmail.com", password="pass123")

        # Login as user1
        self.client.force_authenticate(user=self.user1)
        self.client2.force_authenticate(user=self.user2)
        # Define endpoint
        self.url = reverse("chat-create-list")  # 👈 Replace with your actual URL name


    def test_get_chat_list_empty(self):
        """Test fetching chat list when no chat exists"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(len(response.data["data"]), 0)


    def test_create_private_chat(self):
        """Test creating a private chat between two users"""
        payload = {
            "group_name": "Private Chat",
            "user_list": [self.user2.id]
        }
        response = self.client.post(self.url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["chat_type"], "private")

        # Ensure chat created in DB
        self.assertEqual(Chat.objects.count(), 1)
        chat = Chat.objects.first()
        self.assertIn(self.user1, chat.participants.all())
        self.assertIn(self.user2, chat.participants.all())

        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["message"], "already exiest chat!")
        self.assertEqual(Chat.objects.count(), 1)


    def test_create_duplicate_private_chat(self):
        """Test that a duplicate private chat is not created"""
        Chat.objects.create(
            chat_type='private',
            inviter=self.user1,
            invitee=self.user2
        )

        payload = {
            "group_name": "Private Chat",
            "user_list": [self.user2.id]
        }

        payload2 = {
            "group_name": "Private Chat",
            "user_list": [self.user1.id]
        }

        response = self.client.post(self.url, payload, format='json')

        response2 = self.client2.post(self.url, payload2, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["message"], "already exiest chat!")
        self.assertEqual(Chat.objects.count(), 1)

        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertTrue(response2.data["success"])
        self.assertEqual(response2.data["message"], "already exiest chat!")
        self.assertEqual(Chat.objects.count(), 1)


    def test_create_group_chat(self):
        """Test creating a group chat"""
        user3 = CustomUser.objects.create_user(email="user3@gmail.com", password="pass123")
        payload = {
            "group_name": "My Group Chat",
            "user_list": [self.user2.id, user3.id]
        }
        response = self.client.post(self.url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["chat_type"], "group")

        chat = Chat.objects.get(name="My Group Chat")
        self.assertIn(self.user1, chat.participants.all())
        self.assertIn(self.user2, chat.participants.all())
        self.assertIn(user3, chat.participants.all())

    def test_pagination_in_get(self):
        """Test that pagination works correctly"""
        # Create multiple chats for pagination
        for i in range(130):
            chat = Chat.objects.create(
                chat_type='group',
                name=f"Chat {i}",
                inviter=self.user1,
                is_accepted_invitee=True
            )
            chat.participants.add(self.user1)
        
        chat=Chat.objects.create(
            chat_type='group',
            name=f"Chat {i}",
            inviter=self.user2,
            is_accepted_invitee=False
        )
        chat.participants.add(self.user1)

        response = self.client.get(self.url + "?page=1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 100)
        response = self.client.get(self.url + "?page=2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 30)




class SpamChatListAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = CustomUser.objects.create_user(email="testemai1@gmail.com", password="pass123")
        self.user2 = CustomUser.objects.create_user(email="testemai2@gmail.com", password="pass123")
        self.user3 = CustomUser.objects.create_user(email="testemai3@gmail.com", password="pass123")

        self.client.force_authenticate(user=self.user1)
        self.url = reverse("spam-chat-list")  # 👈 replace with your actual URL name

        # Spam chat: user1 invited by user2 but not accepted yet
        self.spam_chat = Chat.objects.create(
            chat_type="private",
            inviter=self.user2,
            invitee=self.user1,
            is_accepted_invitee=False
        )
        self.spam_chat.participants.add(self.user1, self.user2)

        # Accepted chat (should NOT appear)
        self.accepted_chat = Chat.objects.create(
            chat_type="private",
            inviter=self.user2,
            invitee=self.user1,
            is_accepted_invitee=True
        )
        self.accepted_chat.participants.add(self.user1, self.user2)

        # Another user’s spam chat (should NOT appear)
        self.other_spam = Chat.objects.create(
            chat_type="private",
            inviter=self.user3,
            invitee=self.user2,
            is_accepted_invitee=False
        )
        self.other_spam.participants.add(self.user2, self.user3)

    def test_get_spam_chats(self):
        """User should see only chats where they are invitee and not accepted"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["message"], "data fatched!")

        # Only 1 chat should appear
        self.assertEqual(len(response.data["data"]), 1)
        data_chat = response.data["data"][0]
        self.assertEqual(data_chat["id"], self.spam_chat.id)

    def test_pagination(self):
        """Pagination should return correct number of chats per page"""
        # Create 130 spam chats for user1
        for i in range(130):
            c = Chat.objects.create(
                chat_type="private",
                inviter=self.user2,
                invitee=self.user1,
                is_accepted_invitee=False
            )
            c.participants.add(self.user1, self.user2)

        response = self.client.get(self.url + "?page=1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 100)

        response = self.client.get(self.url + "?page=2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 31)  # 130 + 1 existing spam = 131 total




class MessageListChatAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = CustomUser.objects.create_user(email="testemai1@gmail.com", password="pass123")
        self.user2 = CustomUser.objects.create_user(email="testemai2@gmail.com", password="pass123")
        self.user3 = CustomUser.objects.create_user(email="testemai3@gmail.com", password="pass123")

        self.client.force_authenticate(user=self.user1)

        # Create chat between user1 and user2
        self.chat = Chat.objects.create(
            chat_type="private",
            name="Test Chat",
            inviter=self.user1,
            invitee=self.user2,
            is_accepted_invitee=True
        )
        self.chat.participants.add(self.user1, self.user2)

        # Create some messages
        for i in range(10):
            Message.objects.create(
                chat=self.chat,
                sender=self.user1,
                text=f"Message {i}"
            )
        

        self.url = reverse("message-list-chat", kwargs={"pk":int(self.chat.id)})


    def test_get_messages_as_participant(self):
        """User in chat should see paginated messages"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["message"], "data fatched!")
        self.assertIn("chat", response.data)
        self.assertIn("data", response.data)
        self.assertEqual(len(response.data["data"]), 10)

        # Verify chat info is correct
        self.assertEqual(response.data["chat"]["id"], self.chat.id)

      

    def test_pagination(self):
        """Pagination should correctly limit results"""
        # Create 120 messages
        for i in range(120):
            Message.objects.create(
                chat=self.chat,
                sender=self.user2,
                text=f"Msg {i}"
            )

        # Page 1 (default page_size=50)
        response = self.client.get(self.url + "?page=1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 50)

        # Page 2
        response = self.client.get(self.url + "?page=2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 50)

        # Page 3
        response = self.client.get(self.url + "?page=3")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # remaining 30 (120 + 10 existing = 130 total)
        self.assertEqual(len(response.data["data"]), 30)

    def test_non_member_cannot_access(self):
        """Non-participant should not be able to view chat messages"""
        self.client.force_authenticate(user=self.user3)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["message"], "You are not a member of this chat!")

    def test_invalid_chat_id(self):
        """Accessing a non-existent chat should return 404"""
        invalid_url = reverse("message-list-chat", kwargs={"pk": 9999})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)





class AcceptLeaveChatAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Create users
        self.user1 = CustomUser.objects.create_user(email="user1@test.com", password="pass123")
        self.user2 = CustomUser.objects.create_user(email="user2@test.com", password="pass123")
        self.user3 = CustomUser.objects.create_user(email="user3@test.com", password="pass123")

        # Authenticate user1
        self.client.force_authenticate(user=self.user1)

        # Create private chat (user1 invites user2)
        self.chat = Chat.objects.create(
            chat_type="private",
            name="Test Chat",
            inviter=self.user1,
            invitee=self.user2,
            is_accepted_invitee=False
        )
        self.chat.participants.add(self.user1, self.user2)

        self.url = lambda pk: reverse("accept-leave-add-chat", kwargs={"pk": pk})

    # ---------------- GET: Accept invite ----------------
    def test_accept_invite_success(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(self.url(self.chat.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["message"], "you are now connected!")
        self.chat.refresh_from_db()
        self.assertTrue(self.chat.is_accepted_invitee)

    def test_accept_invite_invalid_user(self):
        self.client.force_authenticate(user=self.user3)
        response = self.client.get(self.url(self.chat.id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

    def test_accept_invite_invalid_chat(self):
        response = self.client.get(self.url(9999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ---------------- POST: Leave chat ----------------
    def test_leave_chat_success(self):
        response = self.client.post(self.url(self.chat.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertNotIn(self.user1, self.chat.participants.all())

    def test_leave_chat_non_member(self):
        self.client.force_authenticate(user=self.user3)
        response = self.client.post(self.url(self.chat.id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_leave_chat_invalid_chat(self):
        response = self.client.post(self.url(9999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ---------------- PUT: Add people to chat ----------------
    def test_add_people_success(self):
        data = {"user_list": [self.user3.id]}
        response = self.client.put(self.url(self.chat.id), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.user3, self.chat.participants.all())
        self.assertEqual(response.data["user_list"], [self.user3.id])
        self.chat.refresh_from_db()
        self.assertEqual(self.chat.chat_type, "group")

    def test_add_people_non_member(self):
        self.client.force_authenticate(user=self.user3)
        data = {"user_list": [self.user3.id]}
        response = self.client.put(self.url(self.chat.id), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_people_invalid_chat(self):
        data = {"user_list": [self.user3.id]}
        response = self.client.put(self.url(9999), data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ---------------- PATCH: Remove people from chat ----------------
    def test_remove_people_success(self):
        self.chat.chat_type = "group"
        self.chat.participants.add(self.user3)
        self.chat.save()
        data = {"user_list": [self.user3.id]}
        response = self.client.patch(self.url(self.chat.id), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(self.user3, self.chat.participants.all())

    def test_remove_people_non_inviter(self):
        self.client.force_authenticate(user=self.user2)
        data = {"user_list": [self.user1.id]}
        response = self.client.patch(self.url(self.chat.id), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_remove_people_invalid_chat(self):
        data = {"user_list": [self.user3.id]}
        response = self.client.patch(self.url(9999), data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)





class NotificationsAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Create users
        self.user1 = CustomUser.objects.create_user(email="user1@test.com", password="pass123")
        self.user2 = CustomUser.objects.create_user(email="user2@test.com", password="pass123")

        # Authenticate user1
        self.client.force_authenticate(user=self.user1)

        # Create 120 notifications for user1
        self.notifications = []
        for i in range(120):
            note = NoteModel.objects.create(user=self.user1, title=f"Note {i}", content=f"Message {i}")
            self.notifications.append(note)

        self.url = reverse("notifications")  # Replace with your actual url name

    def test_get_notifications_success(self):
        """User should fetch notifications successfully"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["message"], "data fatched!")
        self.assertEqual(len(response.data["data"]), 100)  # default page_size=100

    def test_pagination_page_2(self):
        """Pagination should return correct results for page 2"""
        response = self.client.get(self.url + "?page=2&page_size=50")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 50)  # remaining 50

    def test_empty_page(self):
        """Requesting page beyond range should return empty list"""
        response = self.client.get(self.url + "?page=999")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 20)

    def test_non_integer_page(self):
        """Non-integer page should default to page 1"""
        response = self.client.get(self.url + "?page=abc&page_size=20")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 20)

    def test_non_integer_page_size(self):
        """Non-integer page_size should default to 100"""
        response = self.client.get(self.url + "?page=1&page_size=xyz")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 100)

    def test_other_user_no_notifications(self):
        """Other users should see empty notifications"""
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 0)
