Behavior description: 
The app will ask the user log in or create an account. 
Once logged in, the user chooses how many questions they want (1–7). The app 
then randomly selects questions. Before answering, the user may type H to reveal
a hint at a cost of 5 points. After each answer the result is shown, the correct 
answer is confirmed if they were wrong, and the user is asked to rate the 
question as Good, Bad, or Skip. At the end of the quiz a summary shows 
the score, accuracy, hints used, then results are saved automatically. From the 
main menu the user can also view their stats at any time, or log out to return 
to the start screen.

Data format:
{
  "questions": [
    {
      "id": 1,
      "question": "Who is credited with inventing the telephone in 1876?",
      "type": "multiple_choice",
      "options": ["Nikola Tesla", "Thomas Edison", "Alexander Graham Bell", 
      "Guglielmo Marconi"],
      "answer": "Alexander Graham Bell",
      "category": "Inventors",
      "hint": "He was born in Scotland and conducted his famous experiment 
      with Watson."
    },
    {
      "id": 2,
      "question": "The World Wide Web was invented by Tim Berners-Lee.",
      "type": "true_false",
      "answer": "true",
      "category": "Modern Inventions",
      "hint": "He proposed it in 1989 while working at CERN."
    },
    {
      "id": 3,
      "question": "What did Marie Curie discover that earned her a Nobel Prize 
      in Physics in 1903?",
      "type": "multiple_choice",
      "options": ["X-rays", "Radioactivity", "Penicillin", "The electron"],
      "answer": "Radioactivity",
      "category": "Science Inventions",
      "hint": "Her work involved uranium and polonium."
    },
    {
      "id": 4,
      "question": "What name is given to the printing method invented by 
      Johannes Gutenberg around 1440?",
      "type": "short_answer",
      "answer": "movable type",
      "category": "Historic Inventions",
      "hint": "It involved individual letter blocks that could be rearranged."
    },
    {
      "id": 5,
      "question": "Thomas Edison invented the first practical light bulb in 
      1879.",
      "type": "true_false",
      "answer": "true",
      "category": "Inventors"
    },
    {
      "id": 6,
      "question": "Which country did Nikola Tesla emigrate to in 1884 to further 
      his electrical research?",
      "type": "multiple_choice",
      "options": ["Germany", "United Kingdom", "United States", "France"],
      "answer": "United States",
      "category": "Inventors",
      "hint": "He eventually worked directly with Thomas Edison after arriving."
    },
    {
      "id": 7,
      "question": "What material did John Pemberton originally market his 1886 
      invention — later known as Coca-Cola — as?",
      "type": "multiple_choice",
      "options": ["An alcoholic spirit", "A patent medicine", "A sports drink",
       "A breakfast tonic"],
      "answer": "A patent medicine",
      "category": "Historic Inventions",
      "hint": "It was originally sold at pharmacies, not restaurants."
    }
  ]
}

File Structure:
quiz.py — The main file you run to start the app
questions.json — The list of quiz questions
requirements.txt — Lists the extra Python packages needed to run the app
data/users.json — Saves usernames and passwords 
data/scores.dat — Saves quiz scores and stats 
modules/auth.py — Takes care of logging in, creating accounts, and keeping
passwords safe
modules/quiz_engine.py — Picks the questions, checks answers, and keeps track of
the score
modules/stats.py — Saves and loads quiz results, and shows the stats screen
modules/feedback.py — Saves question ratings and uses them to decide which 
questions to show next

Error handling:
Error 1 — questions.json is missing or broken
Prints a clear error message telling the user the file is missing or invalid.

Error 2 — Invalid input from the user
Prints "Invalid input. Please try again." and re-shows the prompt.

Error 3 — Not enough questions available
If the user asks for more questions than exist, the app warns them and uses 
however many are available. If a category filter leaves zero questions, the user 
is sent back to pick a different category

Acceptance criteria:
AC1 — Missing question file. If questions.json is deleted, the app shows a 
friendly error message and closes instead of crashing.
AC2 — Login works properly. A new user can make an account, close the app, 
reopen it, and log back in. Their password should not be visible in plain 
text anywhere.
AC3 — Scores are saved. After finishing a quiz, the score and results are 
saved correctly and show up on the stats screen.
AC4 — Hints cost points. Using a hint gives 5 points for a correct answer 
instead of the usual 10, and the number of hints used is shown at the end of 
the quiz.
AC5 — Bad input doesn't break the app. If the user types something unexpected 
at any point, the app just asks them again instead of crashing.
