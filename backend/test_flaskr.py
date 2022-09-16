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
        self.database_name = "trivia_test"
        self.db_username= str(os.environ.get('db_username'))
        self.db_password = str(os.environ.get('db_password')) 
        self.database_path ='postgresql://'+ self.db_username+':'+ self.db_password +'@localhost:5432/'+self.database_name
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
    DONE
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))

    def test_404_filter_category_by_id(self):
        res = self.client().get('/categories/1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource/requested data cannot be found')

    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(len(data['categories']))

    def test_404_filter_questions_by_invalid_page(self):
        res = self.client().get('/questions?page=9000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource/requested data cannot be found')


    def test_delete_question(self):
        # create dummy question
        question = Question(question='This is a test question', answer='This is a test answer',
                            difficulty=1, category=1)
        question.insert()
        
        res = self.client().delete('/questions/'+str(question.id))
        data = json.loads(res.data)

        deleted_question_id = question.id
        question = Question.query.filter(
            Question.id == question.id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(int(data['deleted_question_id']), deleted_question_id)
        self.assertEqual(question, None)

    def test_422_delete_id_that_does_not_exist(self):
        res = self.client().delete('/questions/hello')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "unprocessable: Your request cannot be processed. Please try again later or contact user support.")

    def test_add_question(self):
        question = 'This is a new question'
        answer = 'This is a new answer'
        difficulty = 1
        category = 1
        new_question = {
            'question': question,
            'answer': answer,
            'difficulty': difficulty,
            'category': category
        }
        expected_total_questions= len(Question.query.all())+1
        res = self.client().post('/questions',json=new_question)
        data = json.loads(res.data)
        total_questions_after_add = len(Question.query.all())

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data['question_id'])
        self.assertEqual(data['question'],question)
        self.assertEqual(data['answer'],answer)
        self.assertEqual(data['difficulty'],difficulty)
        self.assertEqual(data['category'],1)
        self.assertEqual(total_questions_after_add, expected_total_questions)

    def test_400_add_question_with_incomplete_body_parameters(self):
        new_question = {
            'question': 'new_question',
            'answer': 'new_answer',
            'category': 1
        }
        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "bad request: Please check your request details. Please try again later or contact user support.")

    def test_search_questions(self):
        search_word = {'searchTerm': 'which'}
        res = self.client().post('/search', json=search_word)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['questions'])
        self.assertTrue(data['totalQuestions'])

    def test_422_search_question_with_empty_string(self):
        search_word = {'searchTerm': ''}
        res = self.client().post('/search', json=search_word)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable: Your request cannot be processed. Please try again later or contact user support.")

    def test_get_questions_per_category(self):
        res = self.client().get('/categories/5/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['totalQuestions'])

    def test_404_get_questions_per_category_with_no_int_values(self):
        res = self.client().get('/categories/a/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource/requested data cannot be found")

    def test_play_quiz(self):
        quiz = {'quiz_category': {'type': 'Sports', 'id': 6},
            'previous_questions': []}

        res = self.client().post('/quizzes', json=quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_422_play_quiz_with_incomplete_body_parameters(self):
        new_quiz_round = {'previous_questions': []}
        res = self.client().post('/quizzes', json=new_quiz_round)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable: Your request cannot be processed. Please try again later or contact user support.")

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()