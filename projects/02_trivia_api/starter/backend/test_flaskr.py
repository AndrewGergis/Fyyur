import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        # self.database_name = "trivia_test"
        # self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)

        self.database_path = 'postgresql://postgres:123@localhost:5432/trivia_test'
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_should_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_categories'] > 0)

    def test_get_categories_404_if_no_categories(self):
        Category.query.delete()
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_should_get_questions_with_page(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertEqual(len(data['questions']), 10)
        self.assertTrue(data['total_questions'] > 0)

    def test_should_get_not_found_questions_if_no_results(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_should_delete_question(self):
        question = Question.query.all()[0]
        res = self.client().delete(f'/questions/{question.id}')
        data = json.loads(res.data)
        deleted_question = Question.query.filter(Question.id == question.id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['id'], question.id)
        self.assertIsNone(deleted_question)

    def test_delete_question_should_return_404(self):
        res = self.client().delete(f'/questions/{1515198}')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_add_question(self):
        new_question = {
            'question': 'Who discovered penicillin?',
            'answer': 'Alexander Fleming',
            'category': 1,
            'difficulty': 3
        }
        res = self.client().post('questions', json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_add_question_400(self):
        new_question = {
            'question': 'Who discovered penicillin?',
            'answer': 'Alexander Fleming',
            'category': 10000,
            'difficulty': 3
        }
        res = self.client().post('questions', json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')

    def test_search_questions(self):
        search_term = {
            'searchTerm': 'what'
        }
        res = self.client().post('/find/questions', json=search_term)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'] > 0)

    def test_search_questions_404(self):
        search_term = {
            'searchTerm': 'Not found question'
        }
        res = self.client().post('/find/questions', json=search_term)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_category_based_questions(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'] > 0)
        self.assertTrue(data['questions'][0]['category'] == 1)

    def test_get_category_based_questions_404(self):
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_quizzes(self):
        request_body = {
            'previous_questions': [1],
            'quiz_category': {
                'id': 1,
                'type': 'Science'
            }
        }
        res = self.client().post('/quizzes', json=request_body)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertNotEqual(data['question']['id'], 1)
        self.assertEqual(data['question']['category'], 1)

    def test_get_quizzes_None_question_if_no_more_questions_in_the_requested_category(self):
        request_body = {
            'previous_questions': [1],
            'quiz_category': {
                'id': 1000,
                'type': 'Science'
            }
        }
        res = self.client().post('/quizzes', json=request_body)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNone(data['question'])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
