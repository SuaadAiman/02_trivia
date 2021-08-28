import os
import unittest
import json
from flask.json import jsonify
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
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres','987654321','localhost:5432', self.database_name)
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
    

    def new_question(self):
        return jsonify({
            'question':'question',
            'answer':'answer',
            'category':'category',
            'difficulty':'difficulty'
        })
    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_paginated_questions(self):
        res1=self.client().get('/questions?page=1')
        data1=json.loads(res1.data)

        res2=self.client().get('/questions?page=2')
        data2=json.loads(res2.data)

        self.assertEqual(res1.status_code,200)
        self.assertEqual(data1['success'], True)
        self.assertTrue(data1['total_questions'])
        self.assertTrue(data1['num_questions_in_page']<=10)
        self.assertTrue(len(data1['categories']))
        self.assertTrue(data1['questions'] != data2['questions'])

    def test_404_requesting_beyond_valid_page(self):
        res=self.client().get('/questions?page=1000',json={'total_questions': '' })
        data=json.loads(res.data)
        
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'not found')
    
    # def test_delete_question(self):

    #     res1=self.client().get('/questions?page=1')
    #     data1=json.loads(res1.data)

    #     res=self.client().delete('/questions/11')
    #     data=json.loads(res.data)

    #     q=Question.query.filter(Question.id == 11).one_or_none()
        
    #     self.assertEqual(res.status_code,200)
    #     self.assertEqual(data['success'],True)
    #     self.assertEqual(data['deleted'],11)
    #     self.assertTrue(data['total_questions'])
    #     self.assertTrue(data['total_questions'] == data1['total_questions']-1)
    #     """self.assertTrue(len(data['current_questions']))"""
    #     self.assertEqual(q,None)


    def test_404_question_notFound(self):
        res=self.client().delete('/questions/1000')
        data=json.loads(res.data)

        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'], 'not found')


    # def test_add_question(self):
    #     res1=self.client().get('/questions?page=1')
    #     data1=json.loads(res1.data)

    #     res=self.client().post('/questions', json={
    #         'question':'question',
    #         'answer':'answer',
    #         'category':1,
    #         'difficulty':1
    #     })
    #     data=json.loads(res.data)
    #     print(data)
    #     q=Question.query.filter(Question.id == data['created']).one_or_none()

    #     self.assertEqual(res.status_code,200)
    #     self.assertEqual(data['success'],True)
    #     self.assertTrue(data['created'])
    #     self.assertTrue(data['total_questions'] == data1['total_questions']+1)
    #     self.assertTrue(q!=None)
    #     """self.assertTrue(len(data['current_questions']))"""
        

    def test_405_if_question_creation_unprocessable(self):
        res=self.client().post('/questions', json={
            'question':'question',
            'answer':'answer',
            'category':'s',
            'difficulty':'ac'
        })
        data=json.loads(res.data)

        self.assertEqual(res.status_code,422)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_405_if_question_creation_not_allowed(self):
        res=self.client().post('/questions/16', json={
            'question':'question',
            'answer':'answer',
            'category':1,
            'difficulty':1
        })
        data=json.loads(res.data)

        self.assertEqual(res.status_code,405)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'], 'method not allowed')
    
    def test_get_question_by_searchTerm(self):
        res=self.client().post('/search', json={'searchTerm':'title'})
        data=json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['questions'])
        self.assertEqual(data['totalQuestions'],2)
    
    def test_get_question_by_searchTerm_noResult(self):
        res=self.client().post('search', json={'searchTerm':'ooooooooo'})
        data=json.loads(res.data)
        
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'], 'not found')


    def test_get_question_by_category(self):
        res=self.client().get('/categories/2/questions')
        data=json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['questions'])
        self.assertEqual(data['totalQuestions'],4)
    
    def test_get_question_by_category_noResult(self):
        res=self.client().get('/categories/10/questions')
        data=json.loads(res.data)

        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'], 'not found')
    
    def test_playing_quizzes_succefully(self):
        res = self.client().post('/quizzes',json={
                "quiz_category": {"type": "History", "id": 4},
                "previous_questions": ['5','9','23']
                })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])
        self.assertEqual(data['totalQuestions'],1)

    def test_playing_quizzes_noQuestions_found(self):
        res = self.client().post('/quizzes',json={
                "quiz_category": {"type": 'c', "id": 10},
                "previous_questions": ['100']
                })
        data = json.loads(res.data)

        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'], 'not found')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()