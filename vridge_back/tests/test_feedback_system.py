"""
VideoPlanet   TDD  
     ,    .
"""

import pytest
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import transaction
from projects.models import Project
from feedbacks.models import FeedBack, FeedBackMessage, FeedBackComment
import json
import time
from concurrent.futures import ThreadPoolExecutor
import websocket

User = get_user_model()


class TestFeedbackDataModel(TestCase):
    """   """
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='test@test.com',
            email='test@test.com',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name=' ',
            user=self.user,
            manager='',
            consumer=''
        )
    
    def test_project_can_have_multiple_feedbacks(self):
        """       """
        #     
        feedback1 = FeedBack.objects.create(project=self.project)
        feedback2 = FeedBack.objects.create(project=self.project)
        
        self.assertEqual(self.project.feedbacks.count(), 2)
        self.assertIn(feedback1, self.project.feedbacks.all())
        self.assertIn(feedback2, self.project.feedbacks.all())
    
    def test_feedback_has_user_and_video(self):
        """     """
        video_file = SimpleUploadedFile("test.mp4", b"video content", content_type="video/mp4")
        feedback = FeedBack.objects.create(
            project=self.project,
            user=self.user,
            video_file=video_file
        )
        
        self.assertEqual(feedback.user, self.user)
        self.assertIsNotNone(feedback.video_file)
        self.assertEqual(feedback.project, self.project)
    
    def test_feedback_comment_with_timestamp(self):
        """    """
        feedback = FeedBack.objects.create(project=self.project, user=self.user)
        comment = FeedBackComment.objects.create(
            feedback=feedback,
            user=self.user,
            timestamp=15.5,  # 15.5 
            content='   ',
            type='technical'
        )
        
        self.assertEqual(comment.timestamp, 15.5)
        self.assertEqual(comment.type, 'technical')


class TestFeedbackAPI(TestCase):
    """ REST API """
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='test@test.com',
            email='test@test.com',
            password='testpass123'
        )
        self.client.login(username='test@test.com', password='testpass123')
        
        self.project = Project.objects.create(
            name=' ',
            user=self.user,
            manager='',
            consumer=''
        )
    
    def test_get_project_feedbacks_list(self):
        """   """
        response = self.client.get(f'/api/projects/{self.project.id}/feedbacks/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('feedbacks', data)
        self.assertIsInstance(data['feedbacks'], list)
    
    def test_create_feedback_with_video(self):
        """   """
        video_file = SimpleUploadedFile("test.mp4", b"video content", content_type="video/mp4")
        
        response = self.client.post(
            f'/api/projects/{self.project.id}/feedbacks/',
            {
                'title': '  ',
                'description': ' ',
                'video_file': video_file
            },
            format='multipart'
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertIn('feedback_id', data)
        self.assertIn('video_url', data)
    
    def test_add_comment_to_feedback(self):
        """  """
        #  
        feedback_response = self.client.post(
            f'/api/projects/{self.project.id}/feedbacks/',
            {'title': ''}
        )
        feedback_id = feedback_response.json()['feedback_id']
        
        #  
        response = self.client.post(
            f'/api/projects/{self.project.id}/feedbacks/{feedback_id}/comments/',
            {
                'timestamp': 10.5,
                'content': '   ',
                'type': 'technical'
            },
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['timestamp'], 10.5)
    
    def test_update_comment(self):
        """ """
        #   
        feedback = FeedBack.objects.create(project=self.project, user=self.user)
        comment = FeedBackComment.objects.create(
            feedback=feedback,
            user=self.user,
            content=' '
        )
        
        #  
        response = self.client.put(
            f'/api/projects/{self.project.id}/feedbacks/{feedback.id}/comments/{comment.id}/',
            {'content': ' '},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        comment.refresh_from_db()
        self.assertEqual(comment.content, ' ')
    
    def test_delete_own_comment(self):
        """  """
        feedback = FeedBack.objects.create(project=self.project, user=self.user)
        comment = FeedBackComment.objects.create(
            feedback=feedback,
            user=self.user,
            content=' '
        )
        
        response = self.client.delete(
            f'/api/projects/{self.project.id}/feedbacks/{feedback.id}/comments/{comment.id}/'
        )
        
        self.assertEqual(response.status_code, 204)
        self.assertFalse(FeedBackComment.objects.filter(id=comment.id).exists())
    
    def test_cannot_delete_others_comment(self):
        """    """
        other_user = User.objects.create_user('other@test.com', 'other@test.com', 'pass')
        feedback = FeedBack.objects.create(project=self.project, user=self.user)
        comment = FeedBackComment.objects.create(
            feedback=feedback,
            user=other_user,
            content='  '
        )
        
        response = self.client.delete(
            f'/api/projects/{self.project.id}/feedbacks/{feedback.id}/comments/{comment.id}/'
        )
        
        self.assertEqual(response.status_code, 403)
        self.assertTrue(FeedBackComment.objects.filter(id=comment.id).exists())


class TestVideoUpload(TestCase):
    """    """
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='test@test.com',
            email='test@test.com',
            password='testpass123'
        )
        self.client.login(username='test@test.com', password='testpass123')
        
        self.project = Project.objects.create(
            name=' ',
            user=self.user,
            manager='',
            consumer=''
        )
    
    def test_chunk_upload_large_video(self):
        """   """
        # 100MB   
        chunk_size = 1024 * 1024  # 1MB
        total_chunks = 100
        
        #   
        response = self.client.post(
            f'/api/projects/{self.project.id}/feedbacks/upload/init/',
            {
                'filename': 'large_video.mp4',
                'total_size': chunk_size * total_chunks,
                'total_chunks': total_chunks
            },
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        upload_id = response.json()['upload_id']
        
        #  
        for i in range(total_chunks):
            chunk_data = b'x' * chunk_size
            response = self.client.post(
                f'/api/projects/{self.project.id}/feedbacks/upload/chunk/',
                {
                    'upload_id': upload_id,
                    'chunk_index': i,
                    'chunk_data': SimpleUploadedFile(f'chunk_{i}', chunk_data)
                },
                format='multipart'
            )
            self.assertEqual(response.status_code, 200)
        
        #  
        response = self.client.post(
            f'/api/projects/{self.project.id}/feedbacks/upload/complete/',
            {'upload_id': upload_id},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        self.assertIn('feedback_id', response.json())
    
    def test_video_encoding_status(self):
        """   """
        #  
        video_file = SimpleUploadedFile("test.mp4", b"video content", content_type="video/mp4")
        response = self.client.post(
            f'/api/projects/{self.project.id}/feedbacks/',
            {'video_file': video_file},
            format='multipart'
        )
        
        feedback_id = response.json()['feedback_id']
        
        #   
        response = self.client.get(
            f'/api/projects/{self.project.id}/feedbacks/{feedback_id}/encoding-status/'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('status', data)
        self.assertIn(data['status'], ['pending', 'processing', 'completed', 'failed'])
    
    def test_get_hls_streaming_url(self):
        """HLS  URL """
        #   (  )
        feedback = FeedBack.objects.create(
            project=self.project,
            user=self.user,
            encoding_status='completed',
            hls_playlist_url='/media/feedback_file/test.m3u8'
        )
        
        response = self.client.get(
            f'/api/projects/{self.project.id}/feedbacks/{feedback.id}/stream/'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('hls_url', data)
        self.assertTrue(data['hls_url'].endswith('.m3u8'))


class TestRealtimeSync(TestCase):
    """  """
    
    def test_websocket_connection(self):
        """WebSocket  """
        ws = websocket.WebSocket()
        ws.connect('ws://localhost:8000/ws/feedback/1/')
        
        #  
        self.assertEqual(ws.connected, True)
        
        #  
        ws.send(json.dumps({
            'type': 'comment.create',
            'data': {
                'timestamp': 10.5,
                'content': ' '
            }
        }))
        
        #  
        response = ws.recv()
        data = json.loads(response)
        self.assertEqual(data['type'], 'comment.created')
        
        ws.close()
    
    def test_concurrent_comment_creation(self):
        """    """
        feedback = FeedBack.objects.create(
            project=self.project,
            user=self.user
        )
        
        def create_comment(user_id):
            user = User.objects.get(id=user_id)
            with transaction.atomic():
                comment = FeedBackComment.objects.create(
                    feedback=feedback,
                    user=user,
                    timestamp=10.0,  #  
                    content=f'User {user_id} comment'
                )
                time.sleep(0.1)  #  
                return comment.id
        
        # 10    
        users = [User.objects.create_user(f'user{i}@test.com', f'user{i}@test.com', 'pass') 
                 for i in range(10)]
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_comment, user.id) for user in users]
            results = [f.result() for f in futures]
        
        #    
        self.assertEqual(feedback.comments.count(), 10)
        
        #    
        timestamps = list(feedback.comments.values_list('timestamp', flat=True))
        self.assertEqual(len(timestamps), len(set(timestamps)))  #  
    
    def test_realtime_cursor_sync(self):
        """  """
        ws1 = websocket.WebSocket()
        ws2 = websocket.WebSocket()
        
        ws1.connect('ws://localhost:8000/ws/feedback/1/')
        ws2.connect('ws://localhost:8000/ws/feedback/1/')
        
        # User1  
        ws1.send(json.dumps({
            'type': 'cursor.move',
            'data': {
                'timestamp': 15.5,
                'x': 100,
                'y': 200
            }
        }))
        
        # User2  
        response = ws2.recv()
        data = json.loads(response)
        
        self.assertEqual(data['type'], 'cursor.moved')
        self.assertEqual(data['data']['timestamp'], 15.5)
        
        ws1.close()
        ws2.close()


class TestPerformance(TestCase):
    """ """
    
    def test_feedback_list_query_performance(self):
        """   """
        # 1000  
        project = Project.objects.create(
            name=' ',
            user=self.user,
            manager='',
            consumer=''
        )
        
        feedbacks = [
            FeedBack(project=project, user=self.user)
            for _ in range(1000)
        ]
        FeedBack.objects.bulk_create(feedbacks)
        
        #   
        start_time = time.time()
        response = self.client.get(f'/api/projects/{project.id}/feedbacks/')
        end_time = time.time()
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(end_time - start_time, 2.0)  # 2 
    
    def test_video_upload_timeout(self):
        """   """
        # 5  
        large_file = SimpleUploadedFile(
            "large.mp4",
            b"x" * (600 * 1024 * 1024),  # 600MB
            content_type="video/mp4"
        )
        
        response = self.client.post(
            f'/api/projects/{self.project.id}/feedbacks/',
            {'video_file': large_file},
            format='multipart'
        )
        
        #   
        self.assertIn(response.status_code, [201, 408])
    
    def test_concurrent_user_limit(self):
        """  100 """
        project = Project.objects.create(
            name=' ',
            user=self.user,
            manager='',
            consumer=''
        )
        
        def simulate_user(user_id):
            ws = websocket.WebSocket()
            ws.connect(f'ws://localhost:8000/ws/feedback/{project.id}/')
            time.sleep(1)  # 1 
            ws.close()
            return True
        
        # 100  
        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(simulate_user, i) for i in range(100)]
            results = [f.result() for f in futures]
        
        self.assertEqual(sum(results), 100)  #  


if __name__ == '__main__':
    pytest.main([__file__, '-v'])