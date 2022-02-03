import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get("page", 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)
    
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response



    @app.route('/categories')
    def retrive_categories():
        categories = {}
        selection = Category.query.order_by(Category.id).all()
      
        for category in selection:
          categories[category.id] = category.type
        
        if len(categories) == 0:
          abort(404)
 
        return jsonify(
          {
            "categories" : categories
          }
        )
    
    @app.route('/questions')
    def retrive_questions():

      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, selection)
      categories_selection =  Category.query.order_by(Category.type).distinct()
      all_categories = {category.id:category.type for category in categories_selection}
      curr_categories = set([question["category"] for question in current_questions])
      current_categories = [all_categories[id] for id in curr_categories ]

      print ("current_questions",current_questions)
      print ("curr_categories",curr_categories)
  

      if len(current_questions) == 0:
        abort(404)

      return jsonify(
        {
          'questions' : current_questions,
          'total_questions': len(selection),
          'categories': all_categories,
          'currentCategory':current_categories

        
        }
      )

    @app.route('/questions/<int:question_id>', methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()

            if question is None:
                abort(404)
            
            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify (
                {
                    "success": True,
                    "deleted": question_id,
                    "questions": current_questions,
                    "total_questions": len(selection)
                }
            
            )
        except:
            abort(422)

    @app.route('/questions', methods=["POST"])
    def add_question():
        body = request.get_json()
        new_question = body.get("question")
        new_answer = body.get("answer")
        new_category = body.get("category")
        new_difficulty = body.get("difficulty")
        search_term = body.get("searchTerm")

        if search_term:
            search_query = Question.query.filter(Question.question.ilike("%{}%".format(search_term))).all()
            found_questions = [question.format() for question in search_query]
            
            return jsonify(
              {
                "questions": found_questions
              }
            )
        else:
            try:
                question = Question(question=new_question,answer=new_answer,difficulty=new_difficulty,category=new_category)
                question.insert()

                selection = Question.query.order_by(Question.id).all()
                current_questions = paginate_questions(request, selection)

                return jsonify(
                  {

                        "success": True,
                        "created": question.id

                  }
                )


            except:
                abort(422)


    @app.route('/categories/<int:category_id>/questions')
    def retrive_questions_by_category(category_id):
        selection = Question.query.filter(Question.category==category_id).all()
        questions = [question.format() for question in selection]
        currentCategory = Category.query.filter(Category.id==category_id).one_or_none()

        if questions:
            return jsonify(
              {
                "questions": questions,
                "total_questions": len(questions),
                "currentCategory": currentCategory.format()

              }
            )



 



     




    '''
    @TODO: 
    Create a GET endpoint to get questions based on category. 

    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    '''


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

    '''
    @TODO: 
    Create error handlers for all expected errors 
    including 404 and 422. 
    '''
    return app

