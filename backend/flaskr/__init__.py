import os
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS,cross_origin
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


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
    @DONE: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    #cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    CORS(app)

    """
    @DONE: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PATCH,POST,DELETE,OPTIONS')
        
        return response


    """
    @DONE:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    @cross_origin()
    def get_categories():
        categories = Category.query.all()

        if len(categories) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'categories': {category.id: category.type for category in categories},
        })

    """
    @DONE:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions')
    @cross_origin()
    def get_questions():
        selection = Question.query.order_by(Question.id).all()
        paginated_questions = paginate_questions(request, selection)
        categories = Category.query.order_by(Category.type).all()

        # questions not available, do not proceed
        if len(paginated_questions) == 0 or None:
            abort(404)

        return jsonify({
            'success': True,
            'questions': paginated_questions,
            'totalQuestions': len(selection),
            'categories': {category.id: category.type for category in categories},
            'currentCategory': None
        })
    
    """
    @DONE:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @cross_origin()
    @app.route("/questions/<question_id>", methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.get(question_id)
            question.delete()
            return jsonify({
                'success': True,
                'deleted_question_id': question_id
            })
        except:
            abort(422)    
    
    """
    @DONE:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route("/questions", methods=['POST'])
    @cross_origin()
    def add_question():
        request_body = request.get_json()

        if not ('question' in request_body and 'answer' in request_body 
        and 'difficulty' in request_body and 'category' in request_body):
            abort(400)

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
    @DONE:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/search', methods=['POST'])
    @cross_origin()
    def search_questions():
        try:
            request_body = request.get_json()
            search_query = request_body.get('searchTerm', '')

            if search_query == '':
                abort(422)
        
            search_results = Question.query.filter(
                    Question.question.ilike(f'%{search_query}%')).all()

            return jsonify({
                'success': True,
                'questions': [each_question.format() for each_question in search_results],
                'totalQuestions': len(search_results)
                }
                )
        except:
            abort(422)
    """
    @DONE:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    @cross_origin()
    def get_questions_by_category(category_id):

        try:
            questions = Question.query.filter(
                Question.category == str(category_id)).all()

            category = Category.query.get(category_id)

            return jsonify({
                'success': True,
                'questions': [question.format() for question in questions],
                'totalQuestions': len(questions),
                'CurrentCategory': category.type
            })
        except:
            abort(422)
    """
    @DONE:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    @cross_origin()
    def play_quiz():

        try:

            request_body = request.get_json()

            # Validate request body has quizz category and previous questions
            if not ('quiz_category' in request_body and 'previous_questions' in request_body):
                abort(422)

            category = request_body.get('quiz_category')
            previous_questions = request_body.get('previous_questions')

            new_questions_in_db = Question.query.filter_by(
                    category=category['id']).filter(Question.id.notin_((previous_questions))).all()

            new_question = new_questions_in_db[random.randrange(
                0, len(new_questions_in_db))].format() if len(new_questions_in_db) > 0 else None

            return jsonify({
                'success': True,
                'question': new_question
            })
        except:
            abort(422)
    """
    @DONE:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource/requested data cannot be found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable: Your request cannot be processed. Please try again later or contact user support."
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request: Please check your request details. Please try again later or contact user support."
        }), 400


    return app

