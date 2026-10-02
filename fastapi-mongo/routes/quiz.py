# app/routes/quiz.py
import pytz
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from quizzly.models.quiz import (
    Quiz,
    QuizCreate,
    QuizStart,
    AnswerSubmission,
    EndQuizRequest,
    QuestionUpdate
)
from quizzly.db.mongodb import db
from quizzly.utils.jwt import get_current_user
from quizzly.utils.gemini import generate_questions
from bson import ObjectId
import random
from quizzly.core.config import settings

IST = pytz.timezone("Asia/Kolkata")
router = APIRouter()


@router.post("/quizzes/create", response_model=Quiz)
async def create_quiz(data: QuizCreate, current_user: dict = Depends(get_current_user)):
    frontend_url = settings.FRONTEND_URL
    quiz_id = str(ObjectId())
    password = random.randint(1000, 9999)
    num_questions = data.num_questions
    subject = data.subject
    topic = data.topic
    difficulty_level = data.difficulty_level
    questions = generate_questions(subject, topic, num_questions, difficulty_level)
    if not questions:
        raise HTTPException(status_code=500, detail="Failed to generate questions")
    quiz_doc = {
        "_id": quiz_id,
        "name": data.name,
        "subject": data.subject,
        "trigger_link": f"{frontend_url}/take-quiz/{quiz_id}",
        "num_questions": num_questions,
        "questions": questions,
        "user_responses": [],
        "taken_by": [],
        "topic": data.topic,
        "difficulty_level": data.difficulty_level,
        "created_by": current_user["id"],
        "created_at": datetime.now(IST).replace(tzinfo=None),
        "start_time": None,
        "end_time": None,
        "exec_time": None,
        "is_started": False,
        "is_executed": False,
        "metadata_fields": {},
        "password": password
    }
    await db.quizzes.insert_one(quiz_doc)
    return quiz_doc


@router.get("/quizzes")
async def get_quizzes():
    quizzes = await db.quizzes.find().to_list(100)
    for quiz in quizzes:
        quiz["_id"] = str(quiz["_id"])
    return quizzes


@router.get("/quizzes/{quiz_id}")
async def get_quiz(quiz_id: str):
    quiz = await db.quizzes.find_one({"_id": quiz_id})
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz


@router.put("/quizzes/{quiz_id}")
async def update_quiz(quiz_id: str, quiz: Quiz):
    await db.quizzes.update_one({"_id": quiz_id}, {"$set": quiz.dict(by_alias=True)})
    return await db.quizzes.find_one({"_id": quiz_id})


@router.delete("/quizzes/{quiz_id}")
async def delete_quiz(quiz_id: str):
    await db.quizzes.delete_one({"_id": quiz_id})
    return {"msg": "Quiz deleted"}


@router.put("/quizzes/{quiz_id}/questions/{index}")
async def update_question(quiz_id: str, index: int, question: QuestionUpdate, current_user: dict = Depends(get_current_user)):
    # Find the quiz
    quiz = await db.quizzes.find_one({"_id": quiz_id})
    
    # Check if quiz exists
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Check if index is valid
    if index < 0 or index >= len(quiz["questions"]):
        raise HTTPException(status_code=404, detail="Question index out of range")
    
    # Check if user is the creator of the quiz
    if quiz["created_by"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="You don't have permission to update this quiz")
    
    # Update question
    question_data = question.dict(exclude_unset=True)
    quiz["questions"][index].update(question_data)
    
    # Save updated quiz
    await db.quizzes.update_one(
        {"_id": quiz_id},
        {"$set": {"questions": quiz["questions"]}}
    )
    
    return {"message": "Question updated successfully", "quiz": quiz}


@router.post("/quizzes/start/{quiz_id}")
async def start_quiz(quiz_id: str, request: QuizStart):
    quiz = await db.quizzes.find_one({"_id": quiz_id})
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    if quiz.get("password") != request.password:
        raise HTTPException(status_code=401, detail="Invalid password")

    if quiz.get("is_started", False):
        return {"message": "Quiz already started", "quiz": quiz}

    start_time = datetime.now(pytz.timezone("Asia/Kolkata")).replace(tzinfo=None)
    await db.quizzes.update_one(
        {"_id": quiz_id},
        {
            "$set": {
                "is_started": True,
                "start_time": start_time,
                "is_executed": False
                },
            "$addToSet": {"taken_by": request.name}
        }
    )

    quiz["start_time"] = start_time
    quiz["is_started"] = True
    return {"message": "Quiz started", "quiz": quiz}


@router.post("/quizzes/{quiz_id}/submit_answers")
async def submit_answers(
    quiz_id: str,
    submission: AnswerSubmission
):
    quiz = await db.quizzes.find_one({"_id": quiz_id})
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    if not quiz.get("is_started", False):
        raise HTTPException(status_code=400, detail="Quiz not started yet")

    if submission.name not in quiz.get("taken_by", []):
        raise HTTPException(status_code=403, detail="User not registered for this quiz")

    questions = quiz["questions"]
    if len(submission.answers) != len(questions):
        raise HTTPException(status_code=400, detail="Number of answers does not match questions")

    # Check if user has already submitted
    if any(resp["name"] == submission.name for resp in quiz.get("user_responses", [])):
        raise HTTPException(status_code=400, detail="Answers already submitted")

    # Evaluate answers
    evaluated_answers = []
    score = 0
    for i, user_ans in enumerate(submission.answers):
        correct = questions[i]["answer"] == user_ans
        evaluated_answers.append({
            "question_index": i,
            "answer": user_ans,
            "is_correct": correct
        })
        if correct:
            score += 1

    # Calculate time taken
    end_time = datetime.now(IST).replace(tzinfo=None)
    start_time = quiz.get("start_time")
    exec_time = (end_time - start_time).total_seconds() if start_time else 0
    exec_time = round(exec_time, 2)

    user_response = {
        "name": submission.name,
        "answers": evaluated_answers,
        "score": score
    }

    await db.quizzes.update_one(
        {"_id": quiz_id},
        {
            "$push": {"user_responses": user_response},
            "$set": {
                "is_executed": True,
                "is_started": False,
                "end_time": end_time,
                "exec_time": exec_time
            }
        }
    )

    return {
        "message": "Answers submitted",
        "score": score,
        "total": len(questions)
    }


@router.post("/quizzes/{quiz_id}/end")
async def end_quiz(quiz_id: str, request: EndQuizRequest):
    quiz = await db.quizzes.find_one({"_id": quiz_id})
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    if not quiz.get("is_started", False):
        raise HTTPException(status_code=400, detail="Quiz has not started yet")

    if quiz.get("is_executed", False):
        raise HTTPException(status_code=400, detail="Quiz already ended")

    user_responses = quiz.get("user_responses", [])
    user_scores = [{"name": user.get("name"), "score": user.get("score", 0)} for user in user_responses ]

    user_response_entry = next(
        (resp for resp in user_responses if resp["name"] == request.name),
        None
    )

    if not user_response_entry:
        raise HTTPException(status_code=400, detail="No responses found for this user")

    questions = quiz.get("questions", [])
    wrong_questions = []
    right_questions = []

    for ans in user_response_entry["answers"]:
        q_idx = ans["question_index"]
        question = questions[q_idx].get("question")
        correct_answer = questions[q_idx].get("answer")
        entry = {
            "question_index": q_idx,
            "question": question,
            "your_answer": ans.get("answer"),
            "correct_answer": correct_answer
        }
        if ans.get("is_correct"):
            right_questions.append(entry)
        else:
            wrong_questions.append(entry)

    score = len(right_questions)
    num_wrong = len(wrong_questions)
    end_time = datetime.now(pytz.timezone("Asia/Kolkata")).replace(tzinfo=None)
    start_time = quiz.get("start_time")
    exec_time = (end_time - start_time).total_seconds() if start_time else 0
    exec_time = round(exec_time, 2)

    await db.quizzes.update_one(
        {"_id": quiz_id, "user_responses.name": request.name},
        {
            "$set": {
                "is_executed": True,
                "is_started": False,
                "end_time": end_time,
                "exec_time": exec_time,
                "user_responses.$.score": score
            }
        }
    )

    return {
        "message": "Quiz ended",
        "user_scores": user_scores,
        "exec_time": exec_time,
        "score": score,
        "number_of_wrong_answers": num_wrong,
        "right_questions": right_questions,
        "wrong_questions": wrong_questions
    }


@router.get("/quizzes/{quiz_id}/leaderboard")
async def get_leaderboard(quiz_id: str):
    quiz = await db.quizzes.find_one({"_id": quiz_id})
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    user_responses = quiz.get("user_responses", [])
    total_questions = len(quiz.get("questions", []))

    leaderboard_data = []
    for response in user_responses:
        score = response.get("score", 0)
        percentage = round((score / total_questions) * 100) if total_questions > 0 else 0
        answers = response.get("answers", [])
        
        # Calculate correct and incorrect answers
        correct_answers = sum(1 for ans in answers if ans.get("is_correct", False))
        incorrect_answers = len(answers) - correct_answers
        
        # Calculate time taken
        time_taken = "N/A"
        exec_time = quiz.get("exec_time")
        if exec_time is not None:
            minutes = int(exec_time // 60)
            seconds = int(exec_time % 60)
            time_taken = f"{minutes}m {seconds}s"
        else:
            end_time = quiz.get("end_time")
            start_time = quiz.get("start_time")
            if end_time is not None and start_time is not None:
                time_diff = (end_time - start_time).total_seconds()
                minutes = int(time_diff // 60)
                seconds = int(time_diff % 60)
                time_taken = f"{minutes}m {seconds}s"

        # Handle end_time properly
        end_time = quiz.get("end_time")
        if end_time is None:
            end_time = datetime.now(IST).replace(tzinfo=None)
        else:
            end_time = end_time.replace(tzinfo=None)

        leaderboard_data.append({
            "id": str(ObjectId()),  # Generate a unique ID for each entry
            "name": response.get("name", "Anonymous"),
            "score": score,
            "percentage": percentage,
            "correctAnswers": correct_answers,
            "incorrectAnswers": incorrect_answers,
            "timeTaken": time_taken,
            "attemptedAt": end_time.isoformat(),
            "answers": answers  # Include detailed answer information
        })

    # Sort by score (highest first), then by time taken (fastest first)
    leaderboard_data.sort(key=lambda x: (-x["score"], x["timeTaken"]))
    return leaderboard_data
