import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
API_URL_PREFIX='/api'
VERSION='/v1.0'

# function to paginate api requests
def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]
    paginated_questions = questions[start:end]
    return paginated_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers','Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods','GET,PATCH,POST,DELETE,OPTIONS')
        return response


    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route(API_URL_PREFIX+VERSION+'/categories')
    def get_categories():
        categories = Category.query.all()

        if len(categories) == 0:
            return jsonify({
                'success': True,
                'categories': [],
        }) 

        return jsonify({
            'success': True,
            'categories': [category.format() for category in categories],
        })

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route(API_URL_PREFIX+VERSION+'/questions')
    def get_questions():
        selection = Question.query.order_by(Question.id).all()
        # questions not available, do not proceed
        if len(selection) == 0:
            abort(404)

        paginated_questions = paginate_questions(request, selection)
        categories = Category.query.order_by(Category.type).all()

        return jsonify({
            'success': True,
            'questions': paginated_questions,
            'total_questions': len(selection),
            'categories': [category.format() for category in categories],
            'current_category': None
        })
    
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route(API_URL_PREFIX+VERSION+"/questions/<question_id>", methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.get(question_id)
            question.delete()
            return jsonify({
                'success': True,
                'deleted_question_id': question_id
            })
        except:
            abort(422,'Error deleting question')    
    
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route(API_URL_PREFIX+VERSION+"/questions", methods=['POST'])
    def add_question():
        request_body = request.get_json()

        if not ('question' in request_body and 'answer' in request_body 
        and 'difficulty' in request_body and 'category' in request_body):
            abort(422)

        try:
            new_question = Question(question=request_body.get('question'), answer=request_body.get('answer'),
                                difficulty=request_body.get('difficulty'), category=request_body.get('category'))
            new_question.insert()

            return jsonify({
                'success': True,
                'question_id': new_question.id,
                'question': new_question.question,
                'answer': new_question.answer,
                'difficulty': new_question.difficulty,
                'category': new_question.category
            })

        except:
            abort(422)
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route(API_URL_PREFIX+VERSION+'/search', methods=['POST'])
    def search_questions():
        try:
            request_body = request.get_json()
            search_query = request_body.get('search_query', None)
        
            if search_query:
                search_results = Question.query.filter(
                    Question.question.ilike(f'%{search_query}%')).all()

                return jsonify({
                    'success': True,
                    'questions': [each_question.format() for each_question in search_results],
                    'total_questions': len(search_results)
                }
                )
        except:
            abort(500)
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    return app

