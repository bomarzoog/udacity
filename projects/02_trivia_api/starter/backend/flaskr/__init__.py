import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  print("page is:",page)
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
    def get_categories():
        categories = {}
        selection = Category.query.order_by(Category.id).all()
      
        for category in selection:
          categories[category.id] = category.type
        
        if len(categories) == 0:
          abort(404)
 
        return jsonify(
          {
            "success": True,
            "categories" : categories
          }
        )
    
    @app.route('/questions')
    def get_questions():

      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, selection)
      categories_selection =  Category.query.order_by(Category.type).distinct()
      all_categories = {category.id:category.type for category in categories_selection}
      curr_categories = set([question["category"] for question in current_questions])
      current_categories = [all_categories[id] for id in curr_categories ]


      if len(current_questions) == 0:
          abort(404)

      return jsonify(
          {
            'success':True,
            'questions' : current_questions,
            'total_questions': len(selection),
            'categories': all_categories,
            'currentCategory':current_categories

        
          }
        )

    @app.route('/questions/<int:question_id>', methods=["DELETE"])
    def delete_question(question_id):
        
        question = Question.query.filter(Question.id == question_id).one_or_none()

        if question is None:
            abort(404)
        try:
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

            if len(found_questions)==0:
                  abort(404)
            else:
                return jsonify(
                    {
                        "questions": found_questions,
                        "total_questions": len(found_questions),
                        "success": True
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
    def get_questions_by_category(category_id):
        selection = Question.query.filter(Question.category==category_id).all()
        questions = [question.format() for question in selection]
        currentCategory = Category.query.filter(Category.id==category_id).one_or_none()

        if len(questions)==0:
            abort(404)

        if questions:
            return jsonify(
              {
                "success":True,
                "questions": questions,
                "total_questions": len(questions),
                "currentCategory": currentCategory.format()["type"]

              }
            )
    
    @app.route('/quizzes', methods=["POST"])
    def play_quizzes():

        body = request.get_json()
        category = body.get("quiz_category")
        previous_questions = body.get("previous_questions")

        try:


            if category['id'] == 0:
                selection = Question.query.all()
            else:
                selection = Question.query.filter(Question.category==category['id']).all()

            questions = [question.format() for question in selection]
            random_question = random.choice(questions)
            print("presvious questions: ", previous_questions)
            print("random id is : ",random_question['id'])


            if( random_question['id'] in previous_questions ):
                new_questions = [question for question in questions if not (question['id'] in previous_questions)]
                random_question = random.choice(new_questions)
                print("new questions is: ",new_questions)
                print("new random question is:",random_question)
        
        
            return jsonify(
                {
                  "success":True,
                  "question": random_question
                }
            )
        except:
            abort(404)


    @app.errorhandler(404)
    def not_found(error):
      return (
          jsonify({"success": False, "error":404, "message": "Page not found"}),
          404
      )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422
        )
     
    @app.errorhandler(405)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 405, "message": "method not allowed"}),
            405
        )
     
            


    return app

