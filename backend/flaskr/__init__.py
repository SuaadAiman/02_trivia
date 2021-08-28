import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import Pagination, SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTION')
        return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
    """categories=[category.format() for category in Category.query.all()]"""
    categories={}
    for category in Category.query.all():
      categories.update({str(category.id):category.type})
    if len(categories)== 0:
      abort(404)
    return jsonify({
                    'success': True,
                    'categories':categories})

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 


  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.

  ///////////Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def questions():
    questions=Question.query.all()
    page=request.args.get('page',1,type=int)
    start=(page - 1) *10
    end=start +10
    """current_questions=[Question.format() for Question in questions]"""
    
    current_questions=questions[start:end]
    if len(current_questions)== 0:
      abort(404)
    categories={}
    for category in Category.query.all():
      categories.update({str(category.id):category.type})
    questions_list=[]
    for q in Question.query.all():
      questions_list.append({
            'id': q.id,
            'question': q.question,
            'answer': q.answer, 
            'difficulty': q.difficulty,
            'category': q.category
        })
    j= jsonify({
      'success': True,
      'questions': questions_list[start:end],
      'total_questions': len(Question.query.all()),
      'num_questions_in_page': len(questions_list[start:end]),
      'categories': categories})
    

    return j
    ''''''
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):

      if(request.method != 'DELETE'):
        abort(405)
    # try:
      q=Question.query.filter_by(id=question_id).one_or_none()
    
      if q is None:
        abort(404)
      else:
        q.delete()

      category_type = Category.query.get(q.category).type

      return jsonify({
      'success': True,
      'deleted': q.id,
      'current_category': category_type,
      'total_questions': len(Question.query.all())
      })
    #except:
    #  abort(422)
    

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def add_question():
    body = request.get_json()
    question_text=body.get('question',None)
    answer=body.get('answer',None)
    catigory_text=body.get('category',None)
    difficulty_score=body.get('difficulty',None)
    
    try:
      q= Question(question=question_text , answer=answer , category=catigory_text ,difficulty=difficulty_score)
      
      q.insert()
    except:
      abort(422)
    
    category_type = Category.query.get(catigory_text).type

    return jsonify({
     'success': True,
     'created': q.id,
     'current_category': category_type,
     'total_questions': len(Question.query.all()),
      
    })

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/search' , methods=['POST'])
  def search_question_basedOn_term():
    body=request.get_json()
    searchTerm=body.get('searchTerm')
    questions_list=[]
    if Question.query.filter(Question.question.ilike("%" + searchTerm + "%")).all()==[]:
      abort(404)
    for q in Question.query.filter(Question.question.ilike("%" + searchTerm + "%")).all():
      questions_list.append({
            'id': q.id,
            'question': q.question,
            'answer': q.answer, 
            'difficulty': q.difficulty,
            'category': q.category
        })
    
    return jsonify({
      'success': True,
      'questions': questions_list,
      'totalQuestions': len(Question.query.filter(Question.question.ilike("%" + searchTerm + "%")).all()),
      'currentCategory': 'Entertainment'
    })


  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<category1>/questions' , methods=['GET'])
  def search_question_basedOn_category(category1):
    questions_list=[]
    
    if Question.query.filter_by(category=category1).all() == []:
      abort(404)
    for q in Question.query.filter_by(category=category1).all():
      questions_list.append({
            'id': q.id,
            'question': q.question,
            'answer': q.answer, 
            'difficulty': q.difficulty,
            'category': q.category
        })
   
    return jsonify({
    'success': True,
    'questions': questions_list,
    'totalQuestions': len(Question.query.filter_by(category=category1).all()),
    'currentCategory': category1
    })

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

  @app.route('/quizzes' , methods=['POST'])
  def play_quizz():
    body=request.get_json()
    previousQuestions=body.get('previous_questions', [])
    quizCategory=body.get('quiz_category')
    
    questions_list=None
    if quizCategory.get('id')== 0:
      
      quiz_questions=Question.query.filter(Question.id.notin_(previousQuestions)).all()
      totalQuestions=len(quiz_questions)
      
      q = random.choice(quiz_questions)
      print(previousQuestions)
      print(quizCategory)
      print(q)
      questions_list={
            'id': q.id,
            'question': q.question,
            'answer': q.answer, 
            'difficulty': q.difficulty,
            'category': q.category
        }

        
    else:
      quiz_questions=Question.query.filter(Question.category==quizCategory.get('id') , Question.id.notin_(previousQuestions)).all()
      if Question.query.filter(Question.category==quizCategory.get('id')).all()== []:
        abort(404)
      totalQuestions=len(quiz_questions)
      print(quiz_questions)
      
      q=random.choice(quiz_questions)
      questions_list={
            'id': q.id,
            'question': q.question,
            'answer': q.answer, 
            'difficulty': q.difficulty,
            'category': q.category
        }
        

    
    return jsonify({
      'success': True,
      'question': questions_list,
      'totalQuestions': totalQuestions,
      'currentCategory': quizCategory.get('type')
    })


  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "unprocessable"
      }), 422

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "not found"
      }), 404

  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      "success": False, 
      "error": 405,
      "message": "method not allowed"
      }), 405
  
  return app

    