import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
    CORS(app)

    '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, DELETE, PUT, PATCH, OPTIONS')
        return response

    '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''

    @app.route('/categories')
    def get_categories():
        categories = Category.query.all()
        if len(categories) == 0:
            abort(404)
        formatted_categories = [c.format() for c in categories]
        categories_dic = {}
        for category in formatted_categories:
            categories_dic[category['id']] = category['type']
        return jsonify({
            'categories': categories_dic,
            'total_categories': len(formatted_categories),
            'success': True
        })

    '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 



  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

    @app.route('/questions')
    def get_questions():
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * 10
        end = start + 10

        questions = Question.query.all()
        formatted_questions = [q.format() for q in questions]

        if len(formatted_questions[start:end]) == 0:
            abort(404)

        categories = Category.query.all()
        formatted_categories = [c.format() for c in categories]

        categories_dic = {}
        for category in formatted_categories:
            categories_dic[category['id']] = category['type']

        print(formatted_questions)
        print(formatted_categories)
        print(categories_dic)

        return jsonify({
            'questions': formatted_questions[start:end],
            'total_questions': len(questions),
            'categories': categories_dic,
            'current_category': formatted_questions[0]['category'],
            'success': True
        })

    '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.get(question_id)

        if question is None:
            abort(404)

        print(question)
        question.delete()

        return jsonify({
            'success': True,
            'id': question_id
        })

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
        print(request.json)
        question = request.json.get('question')
        answer = request.json.get('answer')
        category_id = request.json.get('category')
        difficulty = request.json.get('difficulty')

        category = Category.query.filter(Category.id == category_id).one_or_none()
        if category is None:
            abort(400)

        new_question = Question(question=question, answer=answer, category=category_id, difficulty=difficulty)
        new_question.insert()
        print(new_question)
        return jsonify({
            'success': True,
            'id': new_question.id
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

    @app.route('/find/questions', methods=['POST'])
    def search_questions():
        print(request.json)
        search_term = request.json.get('searchTerm')
        questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()

        if len(questions) == 0:
            abort(404)

        formatted_questions = [q.format() for q in questions]
        print(formatted_questions)
        categories = Category.query.all()
        formatted_categories = [c.format() for c in categories]

        categories_dic = {}
        for category in formatted_categories:
            categories_dic[category['id']] = category['type']

        return jsonify({
            'questions': formatted_questions,
            'total_questions': len(questions),
            'categories': categories_dic,
            'current_category': formatted_questions[0]['category'],
            'success': True
        })

    '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

    @app.route('/categories/<int:category_id>/questions')
    def get_category_based_questions(category_id):
        print(request.json)
        questions = Question.query.filter(Question.category == category_id).all()
        formatted_questions = [q.format() for q in questions]
        print(formatted_questions)
        if len(formatted_questions) == 0:
            abort(404)

        categories = Category.query.all()
        formatted_categories = [c.format() for c in categories]

        categories_dic = {}
        for category in formatted_categories:
            categories_dic[category['id']] = category['type']

        return jsonify({
            'questions': formatted_questions,
            'total_questions': len(questions),
            'categories': categories_dic,
            'current_category': formatted_questions[0]['category'],
            'success': True
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

    @app.route('/quizzes', methods=['POST'])
    def get_quizzes():
        previous_questions = request.json.get('previous_questions')
        print(previous_questions)
        quiz_category = request.json.get('quiz_category')
        print(quiz_category)

        if quiz_category['id'] == 0:
            questions = Question.query.all()
        else:
            questions = Question.query.filter(Question.category == quiz_category['id']).all()

        formatted_questions = [q.format() for q in questions]

        valid_questions = []
        for question in formatted_questions:
            if question['id'] not in previous_questions:
                valid_questions.append(question)

        print(valid_questions)

        if len(valid_questions) > 0:
            question = random.choice(valid_questions)
        else:
            question = None

        return jsonify({
            'success': True,
            'question': question
        })

    '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

    @app.errorhandler(400)
    def bad_request(error):
        print(error)
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'bad request'
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        print(error)
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'resource not found'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        print(error)
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'unprocessable'
        }), 422

    @app.errorhandler(500)
    def unprocessable(error):
        print(error)
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'something went wrong, server error.'
        }), 500

    @app.errorhandler(405)
    def not_allowed(error):
        print(error)
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'method not allowed'
        }), 405

    return app
