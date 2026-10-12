import streamlit as st
import database
import json
import random
import os
import requests
from urllib.parse import quote_plus
from dotenv import load_dotenv
from google import genai

load_dotenv()

st.set_page_config(
    page_title="SkillPath AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load the external SkillPath AI theme.
from pathlib import Path

css_path = Path(__file__).parent / "style.css"

if css_path.exists():
    with open(css_path, "r", encoding="utf-8") as css_file:
        css_content = css_file.read()

    st.markdown(
        f"<style>{css_content}</style>",
        unsafe_allow_html=True
    )

database.init_db()


# =========================================================
# SKILL ASSESSMENT QUESTION BANKS
# =========================================================

question_banks = {
    "Software Development": [
        ("Which Python type stores key-value pairs?", ["List", "Tuple", "Dictionary", "Set"], 2, "A dictionary stores key-value pairs."),
        ("Which data structure follows FIFO?", ["Stack", "Queue", "Tree", "Graph"], 1, "A queue follows First In, First Out."),
        ("What is binary search complexity?", ["O(n)", "O(log n)", "O(n²)", "O(n log n)"], 1, "Binary search halves the search space."),
        ("Which SQL command retrieves data?", ["SELECT", "UPDATE", "DELETE", "INSERT"], 0, "SELECT retrieves records."),
        ("Which OOP concept allows a class to reuse another class?", ["Looping", "Inheritance", "Iteration", "Casting"], 1, "Inheritance supports code reuse."),
        ("Which Python keyword defines a function?", ["func", "define", "def", "function"], 2, "Python functions are defined using def."),
        ("Which structure uses LIFO?", ["Queue", "Stack", "Array", "Graph"], 1, "A stack follows Last In, First Out."),
        ("Which operator checks equality in Python?", ["=", "==", "!=", ":="], 1, "Double equals compares values."),
        ("What is the usual index of the first Python list item?", ["0", "1", "-1", "Depends always"], 0, "Python sequences are zero-indexed."),
        ("Which SQL clause filters rows?", ["ORDER BY", "WHERE", "GROUP BY", "JOIN"], 1, "WHERE filters records."),
        ("Which keyword handles exceptions?", ["catch", "error", "except", "final"], 2, "except handles matching exceptions."),
        ("What does an API allow?", ["Systems to communicate", "Only styling", "Only printing", "Only file deletion"], 0, "APIs define ways for software to interact."),
        ("Which is a mutable Python collection?", ["Tuple", "String", "List", "Integer"], 2, "Lists can be modified."),
        ("What is a primary key?", ["A duplicate field", "A unique row identifier", "A chart", "A loop"], 1, "A primary key identifies a row uniquely."),
        ("What is unit testing?", ["Testing small code units", "Buying software", "Designing logos", "Installing an OS"], 0, "Unit tests check individual functions or components."),
        ("Which keyword creates a class in Python?", ["object", "class", "new", "struct"], 1, "The class keyword defines a class."),
        ("Which data structure is commonly used for recursion?", ["Queue", "Stack", "Graph", "Hash table"], 1, "Function calls use a call stack."),
        ("What does a loop do?", ["Repeats instructions", "Deletes a program", "Creates a database only", "Encrypts every file"], 0, "Loops repeat code while a condition or sequence allows."),
        ("What is debugging?", ["Finding and fixing errors", "Writing only comments", "Deleting source code", "Installing a browser"], 0, "Debugging helps identify and fix program errors."),
        ("What is an algorithm?", ["A step-by-step solution", "A computer monitor", "A file extension", "A database password"], 0, "An algorithm describes steps to solve a problem.")
    ],

    "Data Science": [
        ("Which Python library is commonly used for tabular data?", ["Pandas", "Turtle", "Pygame", "Tkinter"], 0, "Pandas provides DataFrame tools."),
        ("What is the median?", ["Most frequent value", "Middle sorted value", "Largest value", "Sum of values"], 1, "The median is the middle value after sorting."),
        ("What does correlation measure?", ["File size", "Relationship between variables", "Row count", "Code speed"], 1, "Correlation measures association between variables."),
        ("Supervised learning uses what?", ["Labelled examples", "No data", "Only images", "Only sorting"], 0, "Supervised learning uses labelled data."),
        ("Which chart can show a numerical distribution?", ["Histogram", "Logo", "Flowchart", "Folder tree"], 0, "Histograms show numerical distributions."),
        ("What does a missing value represent?", ["Unavailable data", "Always zero", "Always an error", "A duplicate"], 0, "Missing values indicate absent observations."),
        ("What is the mean?", ["Sum divided by count", "Middle value", "Most frequent value", "Largest minus smallest"], 0, "The mean is the arithmetic average."),
        ("Which library is commonly used for numerical arrays?", ["NumPy", "Flask", "BeautifulSoup", "Tkinter"], 0, "NumPy supports numerical arrays and operations."),
        ("What is classification?", ["Predicting categories", "Sorting files", "Compressing data", "Drawing layouts"], 0, "Classification predicts class labels."),
        ("What is regression used for?", ["Predicting numerical values", "Only grouping text", "Deleting rows", "Formatting pages"], 0, "Regression predicts continuous values."),
        ("Why split data into train and test sets?", ["Evaluate on unseen data", "Guarantee 100% accuracy", "Remove all features", "Increase file size"], 0, "Test data estimates performance on unseen examples."),
        ("What is an outlier?", ["An unusually distant observation", "The average", "A column name", "A file type"], 0, "Outliers differ substantially from typical observations."),
        ("What does data cleaning involve?", ["Fixing data quality issues", "Deleting every row", "Changing screen colour", "Installing Python"], 0, "Cleaning addresses errors, duplicates and missing data."),
        ("What is clustering?", ["Grouping similar observations", "Predicting labelled classes only", "Sorting numbers only", "Creating passwords"], 0, "Clustering groups similar data points."),
        ("What does a confusion matrix summarise?", ["Classification predictions", "File permissions", "Database size", "Network speed"], 0, "It compares predicted and actual classes."),
        ("What is exploratory data analysis?", ["Examining data to find patterns", "Deleting the dataset", "Writing HTML only", "Installing an operating system"], 0, "EDA helps understand data before modelling."),
        ("What does standard deviation describe?", ["Data spread", "Number of columns only", "File format", "Database password"], 0, "Standard deviation measures the spread of values."),
        ("What is a data frame?", ["A table-like data structure", "A web browser", "A programming loop", "A network cable"], 0, "A DataFrame stores labelled rows and columns."),
        ("What is data visualization?", ["Showing data graphically", "Deleting missing values only", "Encrypting data", "Compiling a program"], 0, "Charts help communicate patterns in data."),
        ("What is overfitting in machine learning?", ["A model fits training data too closely", "A dataset has no rows", "A chart has many colours", "A file is too large"], 0, "Overfitting can reduce performance on unseen data.")
    ],

    "Web Development": [
        ("What does HTML primarily define?", ["Webpage structure", "Database passwords", "Server hardware", "Network cables"], 0, "HTML defines webpage structure."),
        ("What is CSS used for?", ["Styling webpages", "Storing records", "Compiling Python", "Sending emails only"], 0, "CSS controls appearance and layout."),
        ("Which language commonly adds webpage interactivity?", ["JavaScript", "SQL", "CSV", "Markdown"], 0, "JavaScript adds interactive behaviour."),
        ("Which HTTP method commonly retrieves a resource?", ["GET", "DELETE", "PATCH", "TRACE"], 0, "GET requests a resource."),
        ("What is responsive design?", ["Adapting to screen sizes", "Removing all images", "Disabling CSS", "Replacing HTML"], 0, "Responsive layouts adapt to devices."),
        ("Which HTML tag creates a hyperlink?", ["<link>", "<a>", "<p>", "<h1>"], 1, "The anchor tag creates links."),
        ("Which CSS property changes text colour?", ["font-style", "color", "padding", "display"], 1, "The color property sets text colour."),
        ("Which HTML element is used for an image?", ["<img>", "<imagefile>", "<pic>", "<src>"], 0, "The img element embeds images."),
        ("What does DOM stand for?", ["Document Object Model", "Data Order Method", "Digital Output Mode", "Document Open Module"], 0, "The DOM represents a webpage as objects."),
        ("Which JavaScript keyword declares a block-scoped variable?", ["varonly", "let", "dim", "define"], 1, "let declares a block-scoped variable."),
        ("What is a frontend?", ["The user-facing part of an app", "Only the database", "A network cable", "A compiler"], 0, "The frontend is the interface users interact with."),
        ("What does a backend commonly handle?", ["Server-side logic", "Only font colour", "Monitor brightness", "Keyboard layout"], 0, "The backend handles logic and data operations."),
        ("What is JSON commonly used for?", ["Structured data exchange", "Styling text", "Image editing only", "Power management"], 0, "JSON represents structured data."),
        ("Which status code means a successful HTTP request?", ["200", "404", "500", "301"], 0, "HTTP 200 indicates success."),
        ("What does Git help developers do?", ["Track code changes", "Style webpages", "Query images only", "Replace programming"], 0, "Git tracks changes to files."),
        ("Which HTML tag creates a paragraph?", ["<p>", "<divonly>", "<sectioning>", "<para>"], 0, "The p element represents a paragraph."),
        ("What does CSS Flexbox help with?", ["Layout and alignment", "Database storage", "Password encryption", "Server installation"], 0, "Flexbox helps arrange items in a layout."),
        ("What is a URL?", ["A web resource address", "A programming loop", "A database table", "An image editor"], 0, "A URL identifies the location of a resource."),
        ("What is an HTML form used for?", ["Collecting user input", "Styling a database", "Compiling JavaScript", "Changing computer hardware"], 0, "Forms collect information entered by users."),
        ("What does an HTTP 404 status usually mean?", ["Resource not found", "Request succeeded", "Server started", "User logged in"], 0, "HTTP 404 means the requested resource was not found.")
    ],

    "AI/ML Engineering": [
        ("What is a machine-learning dataset?", ["Examples for learning or evaluation", "A webpage theme", "A password", "A hardware cable"], 0, "Datasets provide examples for model development."),
        ("What is a feature?", ["An input variable", "A password", "A file extension", "A chart title"], 0, "Features are model input variables."),
        ("Why split training and test data?", ["Evaluate on unseen examples", "Guarantee perfection", "Remove all labels", "Increase screen brightness"], 0, "Test data helps assess generalisation."),
        ("Which is a classification task?", ["Spam or not spam", "Compressing a folder", "Changing font size", "Renaming a file"], 0, "Classification predicts categories."),
        ("What does accuracy measure?", ["Fraction of correct predictions", "Training file size", "Number of files", "Internet speed"], 0, "Accuracy is the proportion of correct predictions."),
        ("What is overfitting?", ["Learning training data too specifically", "Having no dataset", "Deleting a model", "Sorting rows"], 0, "Overfit models may perform poorly on unseen data."),
        ("What is a label in supervised learning?", ["The target answer", "A file path", "A chart colour", "A loop"], 0, "Labels are the target outputs."),
        ("What does an unsupervised method often do?", ["Find patterns without target labels", "Use only labelled answers", "Compile websites", "Format documents"], 0, "Unsupervised methods explore unlabelled data."),
        ("What is a model?", ["A learned mapping or pattern", "Only a spreadsheet", "A password", "A keyboard"], 0, "A model learns patterns from data."),
        ("What is a training epoch?", ["One pass through training data", "One database column", "A programming language", "A chart type"], 0, "An epoch is one full pass through training data."),
        ("What does precision measure?", ["Correct positive predictions among predicted positives", "All negatives", "File size", "Training duration"], 0, "Precision measures the reliability of positive predictions."),
        ("What does recall measure?", ["Found actual positives among all actual positives", "Number of files", "Model size", "Network speed"], 0, "Recall measures how many actual positives were found."),
        ("What is feature scaling?", ["Putting feature values on comparable scales", "Deleting every feature", "Changing labels randomly", "Making a chart"], 0, "Scaling helps when feature magnitudes differ."),
        ("What is a hyperparameter?", ["A setting chosen before/during model training", "Always a target label", "A row index", "An output file only"], 0, "Hyperparameters control the training process."),
        ("Why use cross-validation?", ["Estimate performance across data splits", "Guarantee no errors", "Remove all features", "Encrypt a dataset"], 0, "Cross-validation evaluates across multiple splits."),
        ("What is a neural network inspired by?", ["Connected processing units", "HTML tags", "Database tables only", "Computer keyboards"], 0, "Neural networks use connected computational units."),
        ("What is a training set?", ["Data used to fit a model", "Only the final report", "A web address", "A programming editor"], 0, "The training set helps a model learn patterns."),
        ("What is a prediction?", ["A model's output for input data", "A database password", "A file extension", "A CSS property"], 0, "A model produces predictions from input features."),
        ("What is a loss function?", ["A measure of model prediction error", "A website menu", "A file manager", "A database username"], 0, "A loss function measures how incorrect predictions are."),
        ("Why is a separate test set useful?", ["It checks performance on unseen data", "It guarantees perfect results", "It replaces all training data", "It removes every feature"], 0, "A separate test set provides an independent evaluation.")
    ]
}


# =========================================================
# PROFILE FORM
# =========================================================


def get_offline_career_guidance(question, career_goal=None):
    question_lower = question.lower()

    if any(word in question_lower for word in ["roadmap", "start", "beginner", "learn"]):
        
        if any(word in question_lower for word in ["web development", "html", "css", "javascript", "website"]):
            return """
## Beginner Web Development Roadmap

1. Learn HTML to create webpage structure.
2. Learn CSS to add colours, layouts and styles.
3. Learn JavaScript to make webpages interactive.
4. Build a simple personal portfolio website.
5. Learn Git and GitHub to save and share your code.
6. Deploy your website using GitHub Pages.

**Today's task:** Create an HTML page with a heading, paragraph and button.
"""

        if career_goal and "data" in career_goal.lower():
            return """
## Beginner Data Science Roadmap

1. Learn Python basics: variables, loops, functions and lists.
2. Practise Pandas and NumPy for data analysis.
3. Learn basic statistics and data visualisation.
4. Build a small project using a CSV dataset.
5. Upload your project and README to GitHub.

**Today's task:** Load a CSV file using Pandas and display its first five rows.
"""
        elif career_goal and "web" in career_goal.lower():
            return """
## Beginner Web Development Roadmap

1. Learn HTML page structure.
2. Practise CSS layouts, colours and responsive design.
3. Learn JavaScript variables, functions and events.
4. Build a portfolio or to-do list website.
5. Upload your project to GitHub.

**Today's task:** Create a simple HTML page with a heading and a button.
"""
        else:
            return """
## Beginner Software Development Roadmap

1. Learn Python or Java fundamentals.
2. Practise variables, conditions, loops and functions.
3. Solve beginner programming problems.
4. Build two small projects.
5. Learn Git and GitHub basics.
6. Practise basic data structures and algorithms.

**Today's task:** Write a program that checks whether a number is even or odd.
"""

    if any(word in question_lower for word in ["project", "projects", "build"]):
        return """
## Beginner Project Ideas

1. Smart To-Do List — HTML, CSS and JavaScript.
2. Expense Tracker — Python or JavaScript.
3. Student Marks Analyzer — Python and Pandas.
4. Personal Portfolio — HTML and CSS.
5. Quiz Application — Python or JavaScript.

Start with one project, test it, and document what you learned.
"""

    if any(word in question_lower for word in ["interview", "placement", "job"]):
        return """
## Placement Preparation Checklist

1. Practise one programming problem daily.
2. Revise arrays, strings, functions and basic data structures.
3. Learn OOP concepts and SQL fundamentals.
4. Prepare a clear explanation of your projects.
5. Maintain your resume and GitHub profile.
6. Practise introducing yourself in simple English.

**Today's task:** Explain one project you have built in 60 seconds.
"""

    return """
## SkillPath AI — Career Guidance

I cannot reach the AI service right now, but you can still make progress.

- **Learn:** Practise programming fundamentals.
- **Build:** Create a small project related to your career goal.
- **Practise:** Solve beginner coding questions.
- **Showcase:** Upload your work to GitHub.

Try asking about a learning roadmap, project ideas, or placement preparation.
"""

def show_profile_form(existing=None, form_key="profile_form"):
    existing = existing or {}

    st.subheader(
        "Edit Your Student Profile" if existing
        else "Create Your Student Profile"
    )
    st.caption("Fields marked * are required.")

    branches = [
        "CSE", "ECE", "EEE", "Mechanical", "Civil",
        "AI & ML", "Data Science", "Other"
    ]
    years = ["1st Year", "2nd Year", "3rd Year", "4th Year", "Other"]

    with st.form(form_key):
        full_name = st.text_input(
            "Full name *",
            value=existing.get("full_name", "")
        )
        college = st.text_input(
            "College name *",
            value=existing.get("college", "")
        )

        old_branch = existing.get("branch", "CSE")
        branch_index = branches.index(old_branch) if old_branch in branches else 0
        branch = st.selectbox("Branch *", branches, index=branch_index)

        old_year = existing.get("year", "1st Year")
        year_index = years.index(old_year) if old_year in years else 0
        year = st.selectbox("Current year *", years, index=year_index)

        phone = st.text_input(
            "Phone number (optional)",
            value=existing.get("phone", "")
        )
        interests = st.text_area(
            "Career interests (comma-separated)",
            value=existing.get("interests", ""),
            placeholder="Web Development, Data Science"
        )
        skills = st.text_area(
            "Skills you know (comma-separated)",
            value=existing.get("skills", ""),
            placeholder="Python, Java, HTML"
        )
        certifications = st.text_area(
            "Certifications (if any)",
            value=existing.get("certifications", "")
        )
        projects = st.text_area(
            "Projects (if any)",
            value=existing.get("projects", "")
        )
        resume_link = st.text_input(
            "Resume link (optional)",
            value=existing.get("resume_link", "")
        )
        github_url = st.text_input(
            "GitHub profile URL (optional)",
            value=existing.get("github_url", "")
        )
        linkedin_url = st.text_input(
            "LinkedIn profile URL (optional)",
            value=existing.get("linkedin_url", "")
        )

        submitted = st.form_submit_button(
            "Save Profile",
            type="primary",
            use_container_width=True
        )

    if submitted:
        if not full_name.strip() or not college.strip():
            st.error("Please enter your full name and college name.")
            return

        data = {
            "full_name": full_name.strip(),
            "college": college.strip(),
            "branch": branch,
            "year": year,
            "phone": phone.strip(),
            "interests": interests.strip(),
            "skills": skills.strip(),
            "certifications": certifications.strip(),
            "projects": projects.strip(),
            "resume_link": resume_link.strip(),
            "github_url": github_url.strip(),
            "linkedin_url": linkedin_url.strip()
        }

        database.save_profile(st.session_state.user_id, data)
        st.success("Your profile has been saved!")
        st.rerun()


# =========================================================
# LOGIN AND SIGNUP
# =========================================================

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if not st.session_state.user_id:
    st.title("🎯 SkillPath AI")
    st.subheader("Your Career. Your Skills. Your Future.")

    login_tab, signup_tab = st.tabs(["Login", "Sign Up"])

    with login_tab:
        with st.form("login_form"):
            login_email = st.text_input(
                "Email address",
                key="login_email"
            )
            login_password = st.text_input(
                "Password",
                type="password",
                key="login_password"
            )
            login_clicked = st.form_submit_button(
                "Login",
                use_container_width=True
            )

        if login_clicked:
            user_id = database.verify_login(
                login_email,
                login_password
            )

            if user_id is not None:
                st.session_state.user_id = user_id
                st.rerun()
            else:
                st.error("Incorrect email or password.")

    with signup_tab:
        with st.form("signup_form"):
            signup_email = st.text_input(
                "Email address",
                key="signup_email"
            )
            signup_password = st.text_input(
                "Create password",
                type="password",
                key="signup_password"
            )
            confirm_password = st.text_input(
                "Confirm password",
                type="password",
                key="confirm_password"
            )
            signup_clicked = st.form_submit_button(
                "Create Account",
                use_container_width=True
            )

        if signup_clicked:
            if signup_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                success, message, user_id = database.register_user(
                    signup_email,
                    signup_password
                )

                if success:
                    st.session_state.user_id = user_id
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

    st.info(
        "New student? Create an account first. "
        "Returning student? Log in with your registered credentials."
    )
    st.stop()


# =========================================================
# REQUIRE PROFILE BEFORE DASHBOARD
# =========================================================

current_profile = database.get_profile(st.session_state.user_id)

if current_profile is None:
    st.title("🎯 Welcome to SkillPath AI!")
    st.write(
        "Your account is ready. "
        "Complete your student profile to continue."
    )
    show_profile_form(form_key="create_profile_form")
    st.stop()


# =========================================================
# MAIN APP HEADER AND SIDEBAR
# =========================================================

st.title("🎯 SkillPath AI")
st.subheader("Your Career. Your Skills. Your Future.")

st.write(
    "An AI-powered career, learning and placement-readiness "
    "platform for engineering students."
)

with st.sidebar:
    st.title("SkillPath AI")
    st.caption("by SkillForge")

    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "My Profile",
            "Career Goals",
            "Skill Assessment",
            "Learning Hub",
            "Jobs & Internships",
            "AI Resume Analyzer",
            "AI Mock Interview",
            "SkillForge Code Lab",
            "SkillForge XP & Achievements",
            "AI Career Mentor",
            "My Progress"
        ]
    )

    st.divider()

    if st.button("Log out", use_container_width=True):
        st.session_state.user_id = None
        st.rerun()

st.divider()


# =========================================================
# DASHBOARD
# =========================================================

if page == "Dashboard":
    st.header("Welcome to your career dashboard!")

    profile = database.get_profile(st.session_state.user_id)
    saved_goal = database.get_career_goal(st.session_state.user_id)
    history = database.get_assessment_history(st.session_state.user_id)

    if profile:
        st.success(f"Welcome, {profile['full_name']}!")

    st.subheader("🎯 Your Career Overview")

    if saved_goal:
        st.info(f"**Your Current Career Goal:** {saved_goal}")
    else:
        st.warning(
            "You haven't selected a career goal yet. "
            "Go to Career Goals to choose one."
        )

    latest_attempt = history[0] if history else None

    if latest_attempt:
        readiness = round(
            latest_attempt["score"]
            / latest_attempt["total_questions"] * 100
        )
        readiness_text = f"{readiness}%"
        assessed_count = str(len(history))
    else:
        readiness_text = "Not assessed"
        assessed_count = "0"

    col1, col2, col3 = st.columns(3)

    col1.metric("Latest Assessment Score", readiness_text)
    col2.metric("Assessments Completed", assessed_count)
    col3.metric("Learning Progress", "Not tracked yet")

    st.divider()
    st.subheader("🚀 Your Career Journey")

    steps = [
        "1. Create your student profile",
        "2. Select your target career",
        "3. Take skill assessments",
        "4. Identify skill gaps",
        "5. Learn through study materials and mock tests",
        "6. Explore matching jobs and internships",
        "7. Track your progress and reassess"
    ]

    for step in steps:
        st.write(step)

    st.divider()
    st.subheader("📌 Your Next Action")

    if not saved_goal:
        st.write("Choose your target career in the Career Goals page.")
    elif not history:
        st.write(
            f"Take the skill assessment for **{saved_goal}** "
            "to establish your starting score."
        )
    else:
        st.write(
            "Review your latest assessment and practise the skills "
            "you need to improve."
        )


# =========================================================
# MY PROFILE
# =========================================================

elif page == "My Profile":
    st.header("My Student Profile")

    profile = database.get_profile(st.session_state.user_id)

    if profile:
        st.write(f"**Name:** {profile['full_name']}")
        st.write(
            f"**Email:** "
            f"{st.session_state.get('user_email', 'Your registered account')}"
        )
        st.write(f"**College:** {profile['college']}")
        st.write(f"**Branch:** {profile['branch']}")
        st.write(f"**Year:** {profile['year']}")
        st.write(f"**Phone:** {profile['phone'] or 'Not added'}")
        st.write(f"**Interests:** {profile['interests'] or 'Not added'}")
        st.write(f"**Skills:** {profile['skills'] or 'Not added'}")
        st.write(
            f"**Certifications:** "
            f"{profile['certifications'] or 'Not added'}"
        )
        st.write(f"**Projects:** {profile['projects'] or 'Not added'}")
        st.write(f"**Resume:** {profile['resume_link'] or 'Not added'}")
        st.write(f"**GitHub:** {profile['github_url'] or 'Not added'}")
        st.write(f"**LinkedIn:** {profile['linkedin_url'] or 'Not added'}")

        with st.expander("✏️ Edit Profile"):
            show_profile_form(
                profile,
                form_key="edit_profile_form"
            )


# =========================================================
# CAREER GOALS
# =========================================================

elif page == "Career Goals":
    st.header("🎯 Choose Your Career Goal")

    st.write(
        "Select the career you want to prepare for. "
        "Your saved student profile will be reused automatically."
    )

    careers = {
        "Software Developer": [
            "Python or Java",
            "Data Structures and Algorithms",
            "Object-Oriented Programming",
            "SQL and Databases",
            "Git and GitHub",
            "Problem Solving"
        ],
        "Web Developer": [
            "HTML",
            "CSS",
            "JavaScript",
            "Responsive Web Design",
            "Git and GitHub",
            "Backend and Database Basics"
        ],
        "Data Scientist": [
            "Python",
            "Statistics and Probability",
            "Pandas and NumPy",
            "Data Visualization",
            "Machine Learning",
            "SQL"
        ],
        "Machine Learning Engineer": [
            "Python",
            "Statistics and Linear Algebra",
            "Data Processing",
            "Machine Learning Algorithms",
            "Model Evaluation",
            "Git and Deployment Basics"
        ],
        "Data Analyst": [
            "SQL",
            "Excel or Spreadsheet Skills",
            "Python",
            "Data Cleaning",
            "Statistics",
            "Data Visualization"
        ],
        "Cybersecurity Analyst": [
            "Networking Fundamentals",
            "Operating Systems",
            "Security Fundamentals",
            "Linux Basics",
            "Python Basics",
            "Log Analysis"
        ],
        "Cloud / DevOps Engineer": [
            "Linux",
            "Networking Fundamentals",
            "Git",
            "Cloud Fundamentals",
            "Scripting",
            "CI/CD and Deployment Basics"
        ]
    }

    saved_goal = database.get_career_goal(
        st.session_state.user_id
    )

    career_options = list(careers.keys())

    if saved_goal in career_options:
        selected_index = career_options.index(saved_goal)
    else:
        selected_index = 0

    with st.form("career_goal_form"):
        selected_career = st.selectbox(
            "Choose your target career",
            career_options,
            index=selected_index
        )

        save_goal_clicked = st.form_submit_button(
            "Save Career Goal",
            type="primary",
            use_container_width=True
        )

    if save_goal_clicked:
        database.save_career_goal(
            st.session_state.user_id,
            selected_career
        )
        st.success(f"Career goal saved: {selected_career}")
        st.rerun()

    st.divider()
    st.subheader("📌 Skills to Prepare")

    st.caption(
        "These are starter recommendations, not a verified "
        "live job-market analysis."
    )

    for skill in careers[selected_career]:
        st.write(f"• {skill}")

    if saved_goal:
        st.info(f"Your currently saved career goal is: {saved_goal}")
    else:
        st.warning("You haven't saved a career goal yet.")


# =========================================================
# SKILL ASSESSMENT
# =========================================================

elif page == "Skill Assessment":
    st.header("🧠 Career Skill Assessment")

    st.write(
        "Answer the questions to check your knowledge. "
        "Your score and attempt history will be saved to your account."
    )

    saved_goal = database.get_career_goal(st.session_state.user_id)

    if saved_goal:
        st.info(f"Your saved career goal: **{saved_goal}**")
    else:
        st.warning(
            "First select a career goal on the Career Goals page. "
            "You can still practise Software Development questions."
        )

    goal_text = (saved_goal or "").lower()

    if "machine learning" in goal_text or "ai/ml" in goal_text or "ml engineer" in goal_text:
        track = "AI/ML Engineering"
    elif "data" in goal_text or "scient" in goal_text or "analyst" in goal_text:
        track = "Data Science"
    elif "web" in goal_text or "frontend" in goal_text:
        track = "Web Development"
    else:
        track = "Software Development"

    st.subheader(f"Assessment: {track}")
    st.caption("15 questions · 1 point per correct answer")

    attempt_key = f"assessment_questions_{track}"

    if st.button("🔄 Start New Attempt"):
        st.session_state.pop(attempt_key, None)
        st.session_state.pop("latest_assessment", None)

        for key in list(st.session_state.keys()):
            if key.startswith(f"assessment_{track}_"):
                del st.session_state[key]

        st.rerun()

    if st.session_state.get(attempt_key) is None:
        # The bank has 20 questions per track.
        # Select a different set of 15 for each new attempt.
        st.session_state[attempt_key] = random.sample(
            question_banks[track],
            k=15
        )

    questions = st.session_state[attempt_key]

    with st.form("career_assessment_form"):
        selected_answers = []

        for i, (question, options, correct, explanation) in enumerate(questions):
            st.markdown(f"**Q{i + 1}. {question}**")

            selected = st.radio(
                f"Choose your answer for question {i + 1}",
                options,
                index=None,
                key=f"assessment_{track}_{i}",
                label_visibility="collapsed"
            )

            selected_answers.append(selected)
            st.divider()

        submitted = st.form_submit_button(
            "Submit Assessment",
            type="primary",
            use_container_width=True
        )

    if submitted:
        if any(answer is None for answer in selected_answers):
            st.warning("Please answer all 15 questions before submitting.")
        else:
            score = sum(
                1
                for i, answer in enumerate(selected_answers)
                if answer == questions[i][1][questions[i][2]]
            )

            goal_to_save = saved_goal or track

            answers_data = [
                {
                    "question": questions[i][0],
                    "your_answer": selected_answers[i],
                    "correct_answer": questions[i][1][questions[i][2]],
                    "is_correct": (
                        selected_answers[i]
                        == questions[i][1][questions[i][2]]
                    ),
                    "explanation": questions[i][3]
                }
                for i in range(len(questions))
            ]

            database.save_assessment(
                st.session_state.user_id,
                goal_to_save,
                score,
                len(questions),
                json.dumps(answers_data)
            )

            st.session_state["latest_assessment"] = {
                "score": score,
                "total": len(questions),
                "answers": answers_data,
                "track": track
            }

            # Clear the submitted attempt's radio selections.
            for key in list(st.session_state.keys()):
                if key.startswith(f"assessment_{track}_"):
                    del st.session_state[key]

            st.session_state.pop(attempt_key, None)
            st.rerun()

    latest = st.session_state.get("latest_assessment")

    if latest:
        st.divider()
        st.subheader("📊 Latest Assessment Result")

        percentage = round(
            latest["score"] / latest["total"] * 100
        )

        st.metric(
            "Your Score",
            f"{latest['score']} / {latest['total']}",
            f"{percentage}%"
        )

        if latest["score"] == latest["total"]:
            st.success("Excellent! You answered every question correctly.")
        elif percentage >= 60:
            st.info("Good start! Review the explanations to improve further.")
        else:
            st.warning(
                "Keep learning and practising. Review the explanations "
                "before your next attempt."
            )

        st.subheader("Review Your Answers")

        for i, answer in enumerate(latest["answers"]):
            with st.expander(
                f"Question {i + 1}: "
                f"{'Correct' if answer['is_correct'] else 'Review needed'}"
            ):
                st.write(f"**Question:** {answer['question']}")
                st.write(f"Your answer: {answer['your_answer']}")
                st.write(f"Correct answer: {answer['correct_answer']}")
                st.write(f"Explanation: {answer['explanation']}")

    st.divider()
    st.subheader("🗂️ Previous Assessment Attempts")

    history = database.get_assessment_history(
        st.session_state.user_id
    )

    if history:
        for attempt in history:
            percentage = round(
                attempt["score"] / attempt["total_questions"] * 100
            )

            st.write(
                f"**{attempt['career_goal']}** — "
                f"{attempt['score']}/{attempt['total_questions']} "
                f"({percentage}%) · {attempt['attempted_at']}"
            )
    else:
        st.caption("Your completed assessments will appear here.")


# =========================================================
# LEARNING HUB
# =========================================================



elif page == "Learning Hub":
    import io
    from xml.sax.saxutils import escape
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer,
        PageBreak, KeepTogether
    )

    st.header("📚 Learning Hub")
    st.write(
        "Learn your chosen career path with course notes, "
        "programming examples, practice exercises and downloadable PDFs."
    )

    # ---------------------------------------------------------
    # COURSE NOTES
    # ---------------------------------------------------------

    courses = {
        "Software Developer": [
            {
                "unit": "Unit 1: Programming Fundamentals",
                "topics": [
                    {
                        "title": "1.1 Introduction to Programming",
                        "notes": """
Programming is the process of writing instructions that a computer
can execute to solve a problem. A programming language provides
rules and keywords for writing these instructions.

A program generally follows three stages:
1. Input: receive data from the user or another source.
2. Processing: perform calculations or apply logic.
3. Output: display or return the result.

An algorithm is a finite sequence of clear steps used to solve a
problem. A flowchart represents these steps using standard symbols.
A programming language converts the solution into executable code.

Common programming languages include Python, Java, C and C++.
Python has simple syntax and is suitable for beginners. Java is
widely used in enterprise applications and backend development.
C helps students understand memory and low-level programming.
""",
                        "code": """name = input("Enter your name: ")
print("Welcome,", name)""",
                        "output": """Enter your name: Tejaswini
Welcome, Tejaswini""",
                        "practice": "Write a program that asks for your name and college, then prints both.",
                        "answer": """name = input("Enter your name: ")
college = input("Enter your college: ")
print("Name:", name)
print("College:", college)""",
                        "interview": "What is an algorithm? An algorithm is a finite, ordered set of steps used to solve a problem."
                    },
                    {
                        "title": "1.2 Variables, Data Types and Operators",
                        "notes": """
A variable is a name used to refer to a value. Variables allow
programs to store and reuse information.

Common Python data types:
• int: whole numbers, such as 10
• float: decimal numbers, such as 3.14
• str: text, such as "Python"
• bool: True or False
• list: an ordered, changeable collection
• tuple: an ordered, unchangeable collection
• dict: key-value pairs

Operators perform operations on values. Arithmetic operators include
+, -, *, /, //, %, and **. Comparison operators include ==, !=, <,
>, <=, and >=. Logical operators include and, or, and not.

The assignment operator = stores a value. The equality operator ==
checks whether two values are equal. These operators have different
purposes and should not be confused.
""",
                        "code": """a = 10
b = 3

print(a + b)
print(a // b)
print(a % b)
print(a > b)""",
                        "output": """13
3
1
True""",
                        "practice": "Create two variables and print their sum, difference, product and quotient.",
                        "answer": """a = 12
b = 4
print(a + b)
print(a - b)
print(a * b)
print(a / b)""",
                        "interview": "What is the difference between = and ==? The first assigns a value; the second compares two values."
                    },
                    {
                        "title": "1.3 Conditions and Loops",
                        "notes": """
Conditional statements allow a program to make decisions. Python
uses if, elif and else to choose which block of code to execute.

A loop repeats a block of code. A for loop is commonly used to
iterate over a sequence or a range. A while loop continues while
its condition remains True.

The break statement terminates a loop. The continue statement skips
the remaining statements in the current iteration. Indentation is
important in Python because it defines code blocks.

Loops are useful for processing lists, calculating totals, searching
data and repeating tasks without writing the same statement many
times.
""",
                        "code": """for number in range(1, 6):
    if number % 2 == 0:
        print(number, "is even")
    else:
        print(number, "is odd")""",
                        "output": """1 is odd
2 is even
3 is odd
4 is even
5 is odd""",
                        "practice": "Write a program to print the multiplication table of a number.",
                        "answer": """n = 5
for i in range(1, 11):
    print(n, "x", i, "=", n * i)""",
                        "interview": "What is the difference between for and while loops? A for loop commonly iterates over a sequence; a while loop repeats while a condition is true."
                    },
                    {
                        "title": "1.4 Functions and Modules",
                        "notes": """
A function is a reusable block of code that performs a specific
task. Functions reduce repetition and make programs easier to test
and maintain.

In Python, def defines a function. Parameters receive input values,
and return sends a result back to the caller. A function may have
zero or more parameters.

A module is a Python file containing reusable code. Modules can be
imported into other programs. Python's standard library includes
modules for mathematics, dates, random values and file handling.

Good functions should have meaningful names and focus on a clear
responsibility. Smaller functions are usually easier to understand,
debug and reuse.
""",
                        "code": """def square(number):
    return number * number

result = square(5)
print(result)""",
                        "output": "25",
                        "practice": "Write a function that returns the larger of two numbers.",
                        "answer": """def larger(a, b):
    if a > b:
        return a
    return b

print(larger(8, 5))""",
                        "interview": "What is the purpose of return? It sends a result from a function back to the code that called it."
                    },
                    {
                        "title": "1.5 Lists, Dictionaries and Strings",
                        "notes": """
A list stores multiple values in an ordered, changeable collection.
List indexing starts at zero. Lists support operations such as
append(), remove(), sort() and slicing.

A dictionary stores key-value pairs. Keys are used to access
corresponding values. Dictionaries are useful for representing
structured information, such as a student's name and marks.

A string is a sequence of characters. Common string operations
include upper(), lower(), strip(), split() and replace(). Strings
are immutable, meaning an existing string cannot be changed in
place; operations create new strings.

Choose a data structure according to the task. Lists are useful
for ordered collections, while dictionaries are useful when values
need to be retrieved using meaningful keys.
""",
                        "code": """student = {
    "name": "Ravi",
    "marks": 85
}

print(student["name"])
print(student["marks"])

numbers = [10, 20, 30]
numbers.append(40)
print(numbers)""",
                        "output": """Ravi
85
[10, 20, 30, 40]""",
                        "practice": "Create a dictionary containing a student's name, branch and year. Print each value.",
                        "answer": """student = {
    "name": "Ravi",
    "branch": "CSE",
    "year": 2
}
for key, value in student.items():
    print(key, ":", value)""",
                        "interview": "What is the difference between a list and a dictionary? A list uses positions for access; a dictionary uses keys."
                    }
                ]
            },
            {
                "unit": "Unit 2: Data Structures and Algorithms",
                "topics": [
                    {
                        "title": "2.1 Arrays, Lists, Stacks and Queues",
                        "notes": """
A data structure organizes data so that it can be accessed and
modified efficiently.

An array stores elements in indexed positions. Python lists provide
a flexible, array-like sequence. A stack follows LIFO: Last In,
First Out. Its common operations are push and pop.

A queue follows FIFO: First In, First Out. Its common operations
are enqueue and dequeue. Queues are useful in scheduling and task
processing. Stacks are useful in undo operations, expression
evaluation and function-call management.

The correct data structure depends on how data must be inserted,
removed, searched and accessed.
""",
                        "code": """stack = []
stack.append(10)
stack.append(20)
stack.append(30)

print(stack.pop())
print(stack)""",
                        "output": """30
[10, 20]""",
                        "practice": "Implement a stack using a Python list and demonstrate push and pop.",
                        "answer": """stack = []
stack.append("A")
stack.append("B")
print("Removed:", stack.pop())
print("Remaining:", stack)""",
                        "interview": "What is LIFO? It means the last item inserted is the first item removed."
                    },
                    {
                        "title": "2.2 Searching and Sorting",
                        "notes": """
Searching locates a target value in a collection. Linear search
checks elements one by one and works on unsorted data. Its worst-case
time complexity is O(n).

Binary search repeatedly divides the search interval into halves.
It requires sorted data and takes O(log n) time in the worst case.

Sorting arranges elements in an order, such as ascending or
descending. Bubble sort repeatedly compares adjacent elements.
Its average and worst-case time complexity is O(n²). More efficient
algorithms, including merge sort, commonly achieve O(n log n).

When choosing an algorithm, consider input size, data order,
memory usage and the required performance.
""",
                        "code": """def binary_search(numbers, target):
    left = 0
    right = len(numbers) - 1

    while left <= right:
        mid = (left + right) // 2

        if numbers[mid] == target:
            return mid
        elif numbers[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1

print(binary_search([2, 4, 6, 8, 10], 8))""",
                        "output": "3",
                        "practice": "Implement linear search and return the index of the target, or -1 if absent.",
                        "answer": """def linear_search(numbers, target):
    for i, value in enumerate(numbers):
        if value == target:
            return i
    return -1

print(linear_search([4, 7, 9], 7))""",
                        "interview": "Why must binary search use sorted data? It decides which half to discard based on the order of elements."
                    },
                    {
                        "title": "2.3 Time and Space Complexity",
                        "notes": """
Time complexity describes how an algorithm's running work grows
as input size increases. Space complexity describes how its memory
requirements grow.

Big O notation expresses an upper-bound growth rate. Common
complexities include O(1), O(log n), O(n), O(n log n) and O(n²).

An O(1) operation takes constant time with respect to input size.
An O(n) algorithm may inspect every element. Nested loops often
produce O(n²) work when each loop depends on the input size.

Complexity analysis helps compare algorithms without relying only
on the speed of one computer. Actual runtime also depends on
implementation, hardware and input characteristics.
""",
                        "code": """numbers = [10, 20, 30, 40]

# One indexed access: O(1)
print(numbers[0])

# One traversal: O(n)
for number in numbers:
    print(number)""",
                        "output": """10
10
20
30
40""",
                        "practice": "Identify the complexity of a loop that visits each element once.",
                        "answer": "The loop has O(n) time complexity because the number of iterations grows linearly with the number of elements.",
                        "interview": "What does O(n) mean? The work grows proportionally to the input size."
                    },
                    {
                        "title": "2.4 Recursion",
                        "notes": """
Recursion occurs when a function calls itself to solve a smaller
version of a problem. Every correct recursive solution needs a
base case to stop recursion and a recursive case that moves toward
that base case.

Recursion is useful for tree traversal, divide-and-conquer
algorithms and mathematical definitions. However, deep recursion
can consume additional call-stack memory and may exceed Python's
recursion limit.

Before using recursion, identify the smallest solvable case and
verify that each recursive call makes progress toward it.
""",
                        "code": """def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

print(factorial(5))""",
                        "output": "120",
                        "practice": "Write a recursive function to calculate the sum of numbers from 1 to n.",
                        "answer": """def total(n):
    if n <= 0:
        return 0
    return n + total(n - 1)

print(total(5))""",
                        "interview": "Why is a base case necessary? It stops recursive calls from continuing indefinitely."
                    },
                    {
                        "title": "2.5 Problem-Solving Approach",
                        "notes": """
A systematic approach makes coding problems easier to solve.

1. Understand the problem and expected output.
2. Identify inputs, constraints and edge cases.
3. Write a simple algorithm or pseudocode.
4. Select appropriate data structures.
5. Implement the solution.
6. Test normal, boundary and invalid cases.
7. Analyse time and space complexity.
8. Improve the solution if necessary.

Practice problems gradually. Begin with arithmetic, strings, lists
and searching before progressing to trees, graphs and dynamic
programming. Explaining your approach is important during interviews.
""",
                        "code": """def is_palindrome(text):
    cleaned = text.lower().replace(" ", "")
    return cleaned == cleaned[::-1]

print(is_palindrome("level"))
print(is_palindrome("hello"))""",
                        "output": """True
False""",
                        "practice": "Write a program that counts the number of vowels in a string.",
                        "answer": """text = "programming"
count = 0
for char in text.lower():
    if char in "aeiou":
        count += 1
print(count)""",
                        "interview": "What are edge cases? They are special inputs, such as empty collections or minimum values, that can reveal errors."
                    }
                ]
            },
            {
                "unit": "Unit 3: Object-Oriented Programming",
                "topics": [
                    {
                        "title": "3.1 Classes and Objects",
                        "notes": """
Object-Oriented Programming (OOP) organizes programs around
objects that combine data and behaviour.

A class is a blueprint defining attributes and methods. An object
is an instance of a class. Attributes store an object's state,
while methods define operations it can perform.

In Python, __init__ initializes a new object. The self parameter
refers to the current instance. Classes are useful when an
application models entities such as students, accounts or products.

OOP can improve organization and reuse when a program contains
related data and behaviour. Small scripts do not always require
classes; choose a design that suits the problem.
""",
                        "code": """class Student:
    def __init__(self, name, branch):
        self.name = name
        self.branch = branch

    def display(self):
        print(self.name, self.branch)

student = Student("Anu", "CSE")
student.display()""",
                        "output": "Anu CSE",
                        "practice": "Create a Book class with title and author attributes.",
                        "answer": """class Book:
    def __init__(self, title, author):
        self.title = title
        self.author = author

book = Book("Python Basics", "Ravi")
print(book.title, book.author)""",
                        "interview": "What is the difference between a class and an object? A class defines a structure; an object is an instance of it."
                    },
                    {
                        "title": "3.2 The Four Principles of OOP",
                        "notes": """
Encapsulation groups data and methods and controls how an object's
state is accessed. Python uses naming conventions and properties
to support controlled access.

Abstraction exposes essential behaviour while hiding implementation
details. Abstract base classes can define interfaces that subclasses
must implement.

Inheritance allows a class to reuse or extend another class's
behaviour. Polymorphism allows different object types to respond
to the same operation in their own ways.

These principles help organize larger programs, but unnecessary
inheritance can make code difficult to maintain. Prefer simple,
clear designs and composition when it fits better.
""",
                        "code": """class Animal:
    def speak(self):
        print("Animal sound")

class Dog(Animal):
    def speak(self):
        print("Woof")

animal = Animal()
dog = Dog()
animal.speak()
dog.speak()""",
                        "output": """Animal sound
Woof""",
                        "practice": "Create a parent Vehicle class and a Car subclass with a different display method.",
                        "answer": """class Vehicle:
    def move(self):
        print("Vehicle moves")

class Car(Vehicle):
    def move(self):
        print("Car drives")

Car().move()""",
                        "interview": "What is polymorphism? It allows the same interface or operation to have different implementations."
                    },
                    {
                        "title": "3.3 Constructors, Methods and Exceptions",
                        "notes": """
A constructor-style initializer such as __init__ sets an object's
initial state. Instance methods operate on an object, while class
methods operate on the class and static methods provide related
functionality without requiring instance state.

Exceptions represent errors or unusual conditions during execution.
try and except can handle expected failures. finally can run cleanup
code regardless of whether an exception occurred.

Handle errors that you can meaningfully respond to. Avoid silently
ignoring every exception because doing so can hide defects.
""",
                        "code": """try:
    number = int("25")
    print(number)
except ValueError:
    print("Invalid number")""",
                        "output": "25",
                        "practice": "Convert user input to an integer and display a helpful message if conversion fails.",
                        "answer": """try:
    number = int(input("Enter an integer: "))
    print(number)
except ValueError:
    print("Please enter a valid integer.")""",
                        "interview": "Why use exception handling? It lets a program respond to expected errors instead of stopping unexpectedly."
                    },
                    {
                        "title": "3.4 Code Reuse and Clean Design",
                        "notes": """
Readable code uses meaningful names, small functions and consistent
formatting. Repeated logic can often be moved into a reusable
function or class.

The Single Responsibility Principle suggests that a module or
class should have one clear reason to change. Modular code makes
testing and debugging easier.

Comments should explain why something is done when the code itself
does not make the reason clear. Avoid comments that merely repeat
obvious statements. Follow established language conventions, such
as Python's PEP 8 style guidance.
""",
                        "code": """def calculate_total(price, quantity):
    return price * quantity

print(calculate_total(50, 3))""",
                        "output": "150",
                        "practice": "Refactor a program with repeated calculations into a reusable function.",
                        "answer": "Create a function with parameters for the changing values, return the result, and call it wherever the calculation is required.",
                        "interview": "Why is modular code useful? It improves readability, reuse, testing and maintenance."
                    },
                    {
                        "title": "3.5 Testing and Debugging",
                        "notes": """
Testing checks whether software behaves as expected. A unit test
checks a small function or component. Integration testing checks
whether components work together. End-to-end testing checks a
complete user workflow.

Debugging is the process of locating and fixing defects. Reproduce
the problem, inspect inputs and outputs, isolate the failing code,
and test the fix.

Automated tests can be repeated after changes to detect regressions.
Tests should include typical inputs, boundary conditions and
expected error cases. Testing reduces risk but cannot prove that
software has no defects.
""",
                        "code": """def add(a, b):
    return a + b

assert add(2, 3) == 5
assert add(-1, 1) == 0
print("All tests passed")""",
                        "output": "All tests passed",
                        "practice": "Write two assertions to test a function that multiplies two numbers.",
                        "answer": """def multiply(a, b):
    return a * b

assert multiply(3, 4) == 12
assert multiply(0, 9) == 0""",
                        "interview": "What is a unit test? It checks one small component in isolation."
                    }
                ]
            },
            {
                "unit": "Unit 4: Databases, SQL and Web Basics",
                "topics": [
                    {
                        "title": "4.1 Database Fundamentals",
                        "notes": """
A database stores organized information. A relational database
stores data in tables made of rows and columns. A row represents
a record; a column represents an attribute.

A primary key uniquely identifies a row. A foreign key connects
related records in different tables. Constraints help maintain
valid data, and normalization reduces unnecessary duplication.

SQL is used to define, query and modify relational databases.
Common systems include SQLite, PostgreSQL, MySQL and SQL Server.
Choose a database according to application requirements, deployment
needs and operational constraints.
""",
                        "code": """CREATE TABLE Students (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    branch TEXT
);

INSERT INTO Students (id, name, branch)
VALUES (1, 'Anu', 'CSE');

SELECT name, branch FROM Students;""",
                        "output": "Example result: Anu | CSE",
                        "practice": "Create an Employees table with an ID, name and salary, then retrieve all records.",
                        "answer": """CREATE TABLE Employees (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    salary REAL
);
SELECT * FROM Employees;""",
                        "interview": "What is a primary key? It uniquely identifies a record in a table."
                    },
                    {
                        "title": "4.2 SQL Queries and Joins",
                        "notes": """
SELECT retrieves data. WHERE filters rows. ORDER BY sorts results.
GROUP BY combines rows into groups, and aggregate functions such
as COUNT, SUM, AVG, MIN and MAX calculate summaries.

INSERT adds records, UPDATE modifies records, and DELETE removes
records. Use WHERE carefully with UPDATE and DELETE to avoid
changing unintended rows.

A JOIN combines related records from multiple tables. INNER JOIN
returns matching rows. LEFT JOIN returns all rows from the left
table and matching rows from the right table, if any.

Parameterized queries should be used when passing user-supplied
values to a database to reduce SQL injection risk.
""",
                        "code": """SELECT branch, COUNT(*) AS total
FROM Students
GROUP BY branch
ORDER BY total DESC;""",
                        "output": "Returns each branch and its student count, ordered from highest to lowest.",
                        "practice": "Write a query to find employees earning more than 30000.",
                        "answer": "SELECT * FROM Employees WHERE salary > 30000;",
                        "interview": "What is a JOIN? It combines related data from two or more tables."
                    },
                    {
                        "title": "4.3 HTTP, APIs and JSON",
                        "notes": """
A web application commonly includes a client and a server. The
client sends an HTTP request; the server processes it and returns
a response.

GET commonly retrieves data. POST commonly submits data. PUT or
PATCH updates resources, and DELETE requests removal.

An API defines how software components communicate. A REST-style
API commonly exposes resources through URLs and HTTP methods.
JSON is a lightweight text format for exchanging structured data.

Common HTTP status codes include 200 for success, 201 for created,
400 for a bad request, 401 for unauthenticated access, 404 for
not found, and 500 for a server error.
""",
                        "code": """import json

student = {
    "name": "Anu",
    "branch": "CSE"
}

text = json.dumps(student)
print(text)
print(json.loads(text)["name"])""",
                        "output": """{"name": "Anu", "branch": "CSE"}
Anu""",
                        "practice": "Create a Python dictionary and convert it into a JSON string.",
                        "answer": """import json
data = {"course": "Python", "level": "Beginner"}
print(json.dumps(data))""",
                        "interview": "What is an API? It is a defined interface through which software components communicate."
                    },
                    {
                        "title": "4.4 HTML, CSS and JavaScript Overview",
                        "notes": """
HTML defines the structure of a web page. Elements such as headings,
paragraphs, links, forms and buttons represent page content.

CSS controls presentation, including layout, spacing, typography
and responsive design. JavaScript adds behaviour, such as validating
forms, responding to clicks and updating page content.

A frontend is the part users interact with. A backend handles
application logic, data access and server-side operations. They
communicate through APIs when required.

A good web interface should be readable, accessible and usable
on different screen sizes.
""",
                        "code": """<!-- HTML example -->
<h1>My First Page</h1>
<p>Welcome to web development.</p>
<button onclick="alert('Hello!')">
    Click Me
</button>""",
                        "output": "A heading, paragraph and button appear on the page. Clicking the button displays a message.",
                        "practice": "Create an HTML page with a heading, paragraph and hyperlink.",
                        "answer": """<!DOCTYPE html>
<html>
<body>
  <h1>My Portfolio</h1>
  <p>I am learning web development.</p>
  <a href="https://example.com">Visit</a>
</body>
</html>""",
                        "interview": "What is the difference between HTML, CSS and JavaScript? They define structure, presentation and behaviour respectively."
                    },
                    {
                        "title": "4.5 Authentication and Data Safety",
                        "notes": """
Authentication verifies who a user is. Authorization determines
what an authenticated user is allowed to do.

Passwords should not be stored as plain text. Production systems
should use established password-hashing libraries and secure
authentication practices. Sessions or tokens can maintain a user's
authenticated state.

Never place database passwords or private API keys in public
frontend code or a public repository. Validate input on the server,
use parameterized SQL queries, and apply access controls to sensitive
data. HTTPS protects data in transit when correctly configured.
""",
                        "code": """# Example validation
email = input("Enter email: ").strip()

if "@" in email and "." in email:
    print("Basic format accepted")
else:
    print("Check the email format")""",
                        "output": "The program accepts a basic email-like format or asks the user to check it.",
                        "practice": "Explain why API keys must not be committed to a public GitHub repository.",
                        "answer": "A public repository may expose the key to others, allowing unauthorized use. Store secrets in environment variables or a secret manager and rotate any exposed keys.",
                        "interview": "What is the difference between authentication and authorization? Authentication verifies identity; authorization checks permissions."
                    }
                ]
            },
            {
                "unit": "Unit 5: Git, Projects and Interviews",
                "topics": [
                    {
                        "title": "5.1 Git and GitHub",
                        "notes": """
Git is a version-control system that records changes to files.
A repository contains project files and their history. A commit
records a snapshot with a message.

GitHub hosts Git repositories online and supports collaboration.
A branch allows work to happen separately from the main line.
Merging combines changes from different branches.

Common commands include git init, git status, git add, git commit,
git log, git branch, git switch, git pull and git push. Understand
the purpose of each command before using it on important work.
""",
                        "code": """git init
git status
git add .
git commit -m "Add first version"
git log""",
                        "output": "Git creates or uses a repository, stages changes, records a commit and displays commit history.",
                        "practice": "Create a repository for a simple Python program and make your first commit.",
                        "answer": "Initialize the repository, add the program, commit it with a meaningful message, then create a remote repository if you want to publish it.",
                        "interview": "What is a commit? It is a recorded snapshot of repository changes."
                    },
                    {
                        "title": "5.2 Building a Complete Project",
                        "notes": """
A project turns concepts into a working solution. Start by
identifying the user problem and defining a small set of features.
Break the work into manageable tasks.

For a Student Task Manager, features might include adding tasks,
marking tasks complete, deleting tasks and saving data. Design
the interface and data model before implementing everything.

Test each feature, handle invalid inputs and document setup steps.
A README should explain the purpose, features, installation,
execution and limitations of the project.

Build a minimum viable version first, then improve it based on
testing and feedback.
""",
                        "code": """tasks = []

def add_task(task):
    if task.strip():
        tasks.append(task.strip())

add_task("Learn Python")
add_task("Practise SQL")
print(tasks)""",
                        "output": "['Learn Python', 'Practise SQL']",
                        "practice": "Plan a small expense tracker with at least three features and explain how each will work.",
                        "answer": "Example features: add an expense with amount and category, list saved expenses, and calculate the total. Validate amounts and store the records in a file or database.",
                        "interview": "What is an MVP? A minimum viable product is a small working version with the core features needed to test an idea."
                    },
                    {
                        "title": "5.3 Deployment and Documentation",
                        "notes": """
Deployment makes an application available in its intended
environment. A static website can be hosted on services such as
GitHub Pages. Python web applications may require a service that
supports a Python runtime.

Before deployment, identify dependencies, environment variables,
file paths and configuration requirements. Keep secrets out of
source code and configure them through the hosting service.

Check application logs and test the deployed URL. A successful
local run does not guarantee that deployment will work because
the remote environment may differ.
""",
                        "code": """# Example requirements.txt
streamlit
pandas
reportlab""",
                        "output": "The file lists Python packages required by the application. Install them with: pip install -r requirements.txt",
                        "practice": "Write a README containing project purpose, features and run instructions.",
                        "answer": "Include the project name, overview, features, prerequisites, installation commands, usage instructions and known limitations.",
                        "interview": "Why are dependencies documented? To help another developer install the packages required to run the project."
                    },
                    {
                        "title": "5.4 Resume and Technical Interviews",
                        "notes": """
A beginner resume should highlight education, relevant skills,
projects, internships and certificates that can be verified.
Describe what you personally implemented and which technologies
you used.

For every project, prepare to explain the problem, your approach,
important code, challenges, testing and future improvements.
Do not claim mastery of technologies that you are still learning.

Technical interviews may cover programming fundamentals, data
structures, OOP, SQL and problem solving. Practise explaining your
reasoning and testing your solution with example inputs.
""",
                        "code": """# Example project description
project = {
    "name": "Smart To-Do List",
    "features": ["Add tasks", "Complete tasks", "Delete tasks"]
}
print(project["name"])""",
                        "output": "Smart To-Do List",
                        "practice": "Prepare a 60-second explanation of one project you have built.",
                        "answer": "Explain the problem, the main features, the tools used, one challenge you solved and one improvement you would make next.",
                        "interview": "How should you describe a project? Explain its purpose, your contribution, implementation choices and what you learned."
                    },
                    {
                        "title": "5.5 Career Roadmap and Practice Plan",
                        "notes": """
A beginner roadmap should be consistent rather than rushed.
First build programming fundamentals. Then practise data structures
and algorithms, learn OOP and SQL, and understand Git.

Next, create two or three small projects. Test them, document them
and publish suitable code to GitHub. Gradually practise interview
questions and learn to explain your decisions clearly.

Example weekly routine:
• 3 days: learn concepts and write small programs
• 2 days: solve programming problems
• 1 day: improve a project
• 1 day: review and revise

Adjust the plan to your college schedule and current level.
Consistency and understanding are more useful than copying code
without knowing how it works.
""",
                        "code": """# Example weekly progress tracker
week = {
    "Python practice": 3,
    "Coding problems": 5,
    "Project features": 1
}
for activity, target in week.items():
    print(activity, ":", target)""",
                        "output": """Python practice : 3
Coding problems : 5
Project features : 1""",
                        "practice": "Create a realistic seven-day study plan for the programming topics you need to learn.",
                        "answer": "Choose a small daily target, reserve time for revision, include practical coding and leave a day to review unfinished tasks.",
                        "interview": "How do you keep learning? Set small goals, practise regularly, review mistakes and build projects that apply new concepts."
                    }
                ]
            }
        ],

        "Web Developer": [
            {
                "unit": "Unit 1: HTML Fundamentals",
                "topics": [
                    {
                        "title": "HTML Structure and Elements",
                        "notes": "HTML defines the structure of a web page using elements. Learn headings, paragraphs, links, images, lists, tables and semantic elements. A standard document includes a doctype, html, head and body. Use meaningful headings and alternative text for images.",
                        "code": "<h1>My Portfolio</h1>\n<p>I am learning web development.</p>\n<a href=\"https://example.com\">Visit</a>",
                        "output": "A heading, paragraph and clickable link appear on the page.",
                        "practice": "Build a personal profile page with a heading, paragraph and link.",
                        "answer": "Use an h1 element for the heading, p for the paragraph and a with an href attribute for the link.",
                        "interview": "HTML provides page structure."
                    },
                    {
                        "title": "Forms and Semantic HTML",
                        "notes": "Forms collect information through input, label, select and button elements. Semantic elements such as header, nav, main, section and footer communicate the meaning of page regions. Labels improve accessibility. Validate important form data on the server as well as in the browser.",
                        "code": "<form>\n  <label for=\"name\">Name</label>\n  <input id=\"name\" name=\"name\" required>\n  <button type=\"submit\">Send</button>\n</form>",
                        "output": "A form with a required name field and submit button.",
                        "practice": "Create a registration form with name and email fields.",
                        "answer": "Use labelled input fields and an appropriate submit button.",
                        "interview": "Semantic HTML uses elements according to their meaning."
                    }
                ]
            },
            {
                "unit": "Unit 2: CSS and Responsive Design",
                "topics": [
                    {
                        "title": "CSS Selectors and Box Model",
                        "notes": "CSS controls page presentation. Selectors target HTML elements. The box model includes content, padding, border and margin. Use consistent spacing, readable fonts and reusable classes. Flexbox and Grid help arrange elements.",
                        "code": "div {\n  padding: 16px;\n  margin: 10px;\n  border: 1px solid #999;\n}",
                        "output": "The div has internal spacing, external spacing and a border.",
                        "practice": "Style a card with a heading, background and spacing.",
                        "answer": "Create a CSS class and apply padding, border-radius and suitable typography.",
                        "interview": "The box model describes content, padding, border and margin."
                    },
                    {
                        "title": "Responsive Layouts",
                        "notes": "Responsive design adapts a page to different screen sizes. Use flexible widths, responsive images, Flexbox, Grid and media queries. A mobile-first design starts with small screens and adds layout changes for larger displays. Test navigation, text and forms on multiple viewport sizes.",
                        "code": "@media (max-width: 600px) {\n  .container { padding: 10px; }\n}",
                        "output": "The container uses reduced padding on screens no wider than 600 pixels.",
                        "practice": "Create a card layout that changes from two columns to one column on mobile.",
                        "answer": "Use CSS Grid with a media query or auto-fit columns.",
                        "interview": "Responsive design makes interfaces work across screen sizes."
                    }
                ]
            },
            {
                "unit": "Unit 3: JavaScript",
                "topics": [
                    {
                        "title": "Variables, Functions and Arrays",
                        "notes": "JavaScript adds behaviour to web pages. Learn let and const, strings, numbers, arrays, objects, conditions, loops and functions. Array methods such as map, filter and find help process collections. Use clear names and test edge cases.",
                        "code": "const nums = [1, 2, 3];\nconst doubled = nums.map(n => n * 2);\nconsole.log(doubled);",
                        "output": "[2, 4, 6]",
                        "practice": "Write a function that returns the largest number in an array.",
                        "answer": "Validate that the array is not empty, then use a loop or Math.max with spread for a suitable small array.",
                        "interview": "const prevents reassignment of the variable binding."
                    },
                    {
                        "title": "DOM and Events",
                        "notes": "The Document Object Model represents the page as objects that JavaScript can access. querySelector selects an element. Event listeners respond to actions such as clicks and form submission. Update text safely and validate user input.",
                        "code": "document.querySelector(\"button\")\n  .addEventListener(\"click\", () => {\n    document.querySelector(\"p\").textContent = \"Hello!\";\n  });",
                        "output": "Clicking the button changes the paragraph text to Hello!",
                        "practice": "Make a button that changes a paragraph when clicked.",
                        "answer": "Select the button and paragraph, register a click listener and update textContent.",
                        "interview": "The DOM lets JavaScript read and modify page elements."
                    }
                ]
            },
            {
                "unit": "Unit 4: Backend and APIs",
                "topics": [
                    {
                        "title": "Server Fundamentals",
                        "notes": "A backend handles requests, application logic and data access. A server listens for HTTP requests and returns responses. Routes map URLs and methods to handlers. Validate inputs and return appropriate status codes. Keep configuration and secrets outside public code.",
                        "code": "const express = require('express');\nconst app = express();\napp.get('/', (req, res) => res.send('Hello'));\napp.listen(3000);",
                        "output": "An Express server responds with Hello at the root URL.",
                        "practice": "Create an endpoint that returns a JSON message.",
                        "answer": "Use res.json({ message: 'Hello' }) inside a route handler.",
                        "interview": "A backend processes requests and application logic."
                    },
                    {
                        "title": "REST APIs and Databases",
                        "notes": "REST-style APIs expose resources through URLs and HTTP methods. JSON is a common data format. Databases persist records beyond a process restart. Use parameterized queries, appropriate access controls and error handling. Never trust client-side validation alone.",
                        "code": "fetch('/api/students')\n  .then(response => response.json())\n  .then(data => console.log(data));",
                        "output": "The browser requests data and logs the returned JSON, if the endpoint responds correctly.",
                        "practice": "Design GET and POST endpoints for a list of tasks.",
                        "answer": "GET retrieves tasks; POST validates and creates a new task.",
                        "interview": "An API defines how software components communicate."
                    }
                ]
            },
            {
                "unit": "Unit 5: Projects and Deployment",
                "topics": [
                    {
                        "title": "Portfolio and Testing",
                        "notes": "A portfolio should show projects, technologies, screenshots and working links. Test navigation, mobile layout, form validation and accessibility. A README should explain the project and how to run it. Be honest about which features you implemented.",
                        "code": "<section>\n  <h2>My Projects</h2>\n  <p>Explore my beginner projects.</p>\n</section>",
                        "output": "A project section appears on the page.",
                        "practice": "Build a portfolio with an About section and two project cards.",
                        "answer": "Use semantic HTML, responsive CSS and tested links.",
                        "interview": "A portfolio provides evidence of practical work."
                    },
                    {
                        "title": "Deployment and Git",
                        "notes": "Git tracks changes and GitHub hosts repositories. Commit meaningful changes and document setup instructions. Static websites can be hosted on GitHub Pages. Check relative paths, asset filenames and build settings when deploying. Never publish private keys.",
                        "code": "git add .\ngit commit -m \"Build portfolio\"\ngit push",
                        "output": "Stages, commits and pushes changes when the repository is configured.",
                        "practice": "Publish a static portfolio and test it on a phone.",
                        "answer": "Commit the site, configure the hosting source, wait for deployment and test the published URL.",
                        "interview": "Deployment makes a project available to its intended users."
                    }
                ]
            }
        ],

        "Data Scientist": [
            {
                "unit": "Unit 1: Python and Data Handling",
                "topics": [
                    {
                        "title": "Python for Data Science",
                        "notes": "Learn variables, functions, loops, lists, dictionaries and file handling. Python is widely used in data science because it has libraries for numerical computation, analysis, visualization and machine learning. Write reusable functions and validate data before analysis.",
                        "code": "values = [10, 20, 30]\nprint(sum(values) / len(values))",
                        "output": "20.0",
                        "practice": "Calculate the average of a list of numbers.",
                        "answer": "Divide the sum of the values by the number of values, checking that the list is not empty.",
                        "interview": "Python supports data analysis through a large ecosystem of libraries."
                    },
                    {
                        "title": "NumPy and Pandas",
                        "notes": "NumPy provides efficient arrays and numerical operations. Pandas provides Series and DataFrames for tabular data. Learn read_csv, head, info, describe, loc, filtering, sorting, groupby and missing-value handling. Inspect data types and data quality before analysis.",
                        "code": "import pandas as pd\ndf = pd.DataFrame({'score': [70, 80, 90]})\nprint(df['score'].mean())",
                        "output": "80.0",
                        "practice": "Load a CSV file and display its first five rows and summary statistics.",
                        "answer": "Use pd.read_csv('file.csv'), df.head() and df.describe().",
                        "interview": "A DataFrame is a two-dimensional labelled table in Pandas."
                    }
                ]
            },
            {
                "unit": "Unit 2: Statistics and Probability",
                "topics": [
                    {
                        "title": "Descriptive Statistics",
                        "notes": "Mean is the arithmetic average. Median is the middle value after sorting. Mode is the most frequent value. Variance measures spread around the mean, while standard deviation is its square root. Outliers can influence the mean more than the median.",
                        "code": "import statistics as s\nvalues = [2, 4, 4, 10]\nprint(s.mean(values))\nprint(s.median(values))",
                        "output": "5\n4.0",
                        "practice": "Calculate mean and median for a small dataset and compare them.",
                        "answer": "Sort the data for the median and add all values then divide by the count for the mean.",
                        "interview": "The median is less sensitive to extreme values than the mean."
                    },
                    {
                        "title": "Probability and Distributions",
                        "notes": "Probability quantifies uncertainty from zero to one. Independent events do not change each other's probabilities. Conditional probability considers information about another event. Common distributions include Bernoulli, binomial and normal distributions. Sampling methods affect conclusions drawn from data.",
                        "code": "favourable = 1\npossible = 6\nprint(favourable / possible)",
                        "output": "0.16666666666666666",
                        "practice": "Find the probability of rolling an even number on a fair six-sided die.",
                        "answer": "There are three even outcomes out of six, so the probability is 3/6 = 0.5.",
                        "interview": "Probability measures how likely an event is."
                    }
                ]
            },
            {
                "unit": "Unit 3: Data Cleaning and Visualization",
                "topics": [
                    {
                        "title": "Data Cleaning",
                        "notes": "Data cleaning addresses missing values, duplicates, inconsistent labels, incorrect types and invalid records. Investigate why values are missing before filling or dropping them. Preserve the original data and document important transformations. Avoid using information from a test dataset to fit preprocessing steps.",
                        "code": "df = df.drop_duplicates()\nprint(df.isnull().sum())",
                        "output": "Displays the number of missing values in each column after removing duplicate rows.",
                        "practice": "Inspect a CSV for duplicates and missing values.",
                        "answer": "Use df.duplicated().sum() and df.isnull().sum(), then decide on a justified treatment.",
                        "interview": "Cleaning improves data consistency but must preserve meaningful information."
                    },
                    {
                        "title": "Charts and Visualization",
                        "notes": "Charts help communicate patterns. Bar charts compare categories, line charts show trends over ordered time, histograms show distributions and scatter plots show relationships between numeric variables. Label axes, include units and avoid misleading scales.",
                        "code": "import matplotlib.pyplot as plt\nplt.bar(['A', 'B'], [10, 15])\nplt.xlabel('Group')\nplt.ylabel('Count')\nplt.show()",
                        "output": "A bar chart comparing counts for groups A and B.",
                        "practice": "Create a bar chart for five categories in a dataset.",
                        "answer": "Choose category labels and values, then plot them with clear axis labels.",
                        "interview": "Choose a chart based on the question and type of data."
                    }
                ]
            },
            {
                "unit": "Unit 4: Machine Learning",
                "topics": [
                    {
                        "title": "Supervised and Unsupervised Learning",
                        "notes": "Supervised learning uses labelled examples for classification or regression. Unsupervised learning finds structure in unlabelled data, such as clusters. Split data into training and testing sets. Fit preprocessing only on training data to reduce leakage. Choose models based on the task and evidence.",
                        "code": "from sklearn.model_selection import train_test_split\nX_train, X_test, y_train, y_test = train_test_split(\n    X, y, test_size=0.2, random_state=42\n)",
                        "output": "Splits features and labels into training and testing subsets, assuming X and y are defined.",
                        "practice": "Explain whether predicting house prices is classification or regression.",
                        "answer": "It is regression because the target is a numeric price.",
                        "interview": "Supervised learning trains on examples with known target labels."
                    },
                    {
                        "title": "Evaluation and Overfitting",
                        "notes": "Classification metrics include accuracy, precision, recall and F1-score. Regression metrics include MAE, MSE and RMSE. Overfitting occurs when a model fits training data too closely and performs poorly on unseen data. Use suitable validation, baseline comparisons and error analysis.",
                        "code": "from sklearn.metrics import accuracy_score\nactual = [1, 0, 1, 1]\npredicted = [1, 0, 0, 1]\nprint(accuracy_score(actual, predicted))",
                        "output": "0.75",
                        "practice": "Explain why accuracy alone can be misleading on an imbalanced dataset.",
                        "answer": "A model can predict the majority class frequently and still achieve high accuracy while missing important minority cases.",
                        "interview": "Overfitting means a model generalizes poorly because it has fitted training-specific patterns."
                    }
                ]
            },
            {
                "unit": "Unit 5: Projects and Communication",
                "topics": [
                    {
                        "title": "End-to-End Data Project",
                        "notes": "A data project defines a question, obtains data, cleans it, explores patterns, builds an analysis or model and evaluates the results. Document assumptions and limitations. A good project explains why the work matters, not only which library was used.",
                        "code": "print('Question -> Data -> Clean -> Analyse -> Evaluate')",
                        "output": "Displays a simple data-project workflow.",
                        "practice": "Choose a public dataset and write three questions to investigate.",
                        "answer": "Pick questions that can be answered using available columns and measurable comparisons.",
                        "interview": "An end-to-end project demonstrates the complete analysis workflow."
                    },
                    {
                        "title": "Presenting Findings",
                        "notes": "Communicate findings with a short summary, clear charts and practical recommendations. Separate observed patterns from causal claims. State limitations and explain uncertainty. Use a README or report so others can reproduce your work.",
                        "code": "finding = 'Group A has a higher average score in this sample.'\nprint(finding)",
                        "output": "Displays a concise finding.",
                        "practice": "Write three sentences describing a chart without claiming causation.",
                        "answer": "Describe the observed comparison, the size or direction of the difference and a limitation.",
                        "interview": "Good communication makes analysis useful to decision-makers."
                    }
                ]
            }
        ],

        "Machine Learning Engineer": [
            {
                "unit": "Unit 1: Python and Mathematics",
                "topics": [
                    {
                        "title": "Python and Numerical Computing",
                        "notes": "Learn functions, classes, data structures and file handling. NumPy arrays support vectorized calculations. Pandas helps inspect and transform datasets. Reproducible scripts should use clear functions, controlled dependencies and documented inputs.",
                        "code": "import numpy as np\nx = np.array([1, 2, 3])\nprint(x * 2)",
                        "output": "[2 4 6]",
                        "practice": "Create an array and calculate its mean.",
                        "answer": "Use np.mean(array).",
                        "interview": "Vectorization applies operations to arrays efficiently."
                    },
                    {
                        "title": "Linear Algebra and Statistics",
                        "notes": "Vectors represent ordered numeric values; matrices organize values in rows and columns. Dot products combine vector elements, and matrix multiplication is used in many models. Mean, variance, probability and derivatives help explain model training and evaluation.",
                        "code": "import numpy as np\nprint(np.dot([1, 2], [3, 4]))",
                        "output": "11",
                        "practice": "Calculate the dot product of two short vectors.",
                        "answer": "Multiply corresponding elements and add the products.",
                        "interview": "A dot product sums products of corresponding vector elements."
                    }
                ]
            },
            {
                "unit": "Unit 2: Data Preparation",
                "topics": [
                    {
                        "title": "Preprocessing and Features",
                        "notes": "Preprocessing can include missing-value treatment, categorical encoding, scaling and feature selection. Fit transformations on training data only and reuse them on validation and test data. A pipeline helps keep preprocessing consistent.",
                        "code": "from sklearn.preprocessing import StandardScaler\nscaler = StandardScaler()\nX_train_scaled = scaler.fit_transform(X_train)",
                        "output": "Learns scaling parameters from X_train and transforms it, assuming X_train is defined.",
                        "practice": "Explain why a test dataset should not be used to fit a scaler.",
                        "answer": "It would leak information from the evaluation data into training.",
                        "interview": "Feature preprocessing converts raw values into a model-ready representation."
                    },
                    {
                        "title": "Data Leakage and Splitting",
                        "notes": "Data leakage occurs when information unavailable at prediction time influences model training or evaluation. Use appropriate splits, including time-based splits for temporal data. Keep labels separate from features and examine duplicate or related records across splits.",
                        "code": "from sklearn.model_selection import train_test_split\nX_train, X_test, y_train, y_test = train_test_split(\n    X, y, test_size=0.2, random_state=42\n)",
                        "output": "Creates training and testing partitions when X and y are defined.",
                        "practice": "Give one example of information that could leak the target.",
                        "answer": "A feature calculated using the target or future information unavailable at prediction time could cause leakage.",
                        "interview": "Leakage produces an overly optimistic estimate of model performance."
                    }
                ]
            },
            {
                "unit": "Unit 3: Algorithms and Evaluation",
                "topics": [
                    {
                        "title": "Core ML Algorithms",
                        "notes": "Linear regression predicts numeric values. Logistic regression estimates class probabilities. Decision trees learn rule-based splits; random forests combine trees. K-means groups observations into clusters. Compare algorithms against a simple baseline and match the algorithm to the problem.",
                        "code": "from sklearn.tree import DecisionTreeClassifier\nmodel = DecisionTreeClassifier(random_state=42)",
                        "output": "Creates a decision-tree classifier; it must be fitted on training data before prediction.",
                        "practice": "Choose an algorithm for predicting a continuous house price.",
                        "answer": "Linear regression is a reasonable baseline for a numeric target.",
                        "interview": "Classification predicts categories; regression predicts numeric values."
                    },
                    {
                        "title": "Metrics and Validation",
                        "notes": "Use accuracy, precision, recall and F1 for classification as appropriate. Use MAE or RMSE for regression. Cross-validation estimates performance across multiple splits. Tune hyperparameters without using the final test set repeatedly.",
                        "code": "from sklearn.metrics import classification_report\n# y_test and predictions must already exist\n# print(classification_report(y_test, predictions))",
                        "output": "The report includes precision, recall, F1-score and support when run with valid labels and predictions.",
                        "practice": "Select a useful metric for detecting a rare but important event.",
                        "answer": "Recall, precision and F1 may be more informative than accuracy, depending on the costs of false positives and false negatives.",
                        "interview": "Validation helps estimate how well a model generalizes."
                    }
                ]
            },
            {
                "unit": "Unit 4: Model Pipelines and Deployment",
                "topics": [
                    {
                        "title": "Pipelines and Model Saving",
                        "notes": "Pipelines combine preprocessing and model steps into one workflow. They reduce inconsistent transformations between training and inference. Save models only in trusted environments and keep track of library versions and training data assumptions.",
                        "code": "from sklearn.pipeline import make_pipeline\nfrom sklearn.preprocessing import StandardScaler\nfrom sklearn.linear_model import LogisticRegression\nmodel = make_pipeline(StandardScaler(), LogisticRegression())",
                        "output": "Creates a preprocessing and classification pipeline that can be fitted on training data.",
                        "practice": "Explain why preprocessing should be included in the model pipeline.",
                        "answer": "It ensures training and inference apply the same transformations.",
                        "interview": "A pipeline connects transformations and an estimator."
                    },
                    {
                        "title": "Serving Predictions",
                        "notes": "A prediction service receives validated input, applies the same preprocessing and returns model predictions. Define an input schema, handle errors and measure latency. Protect sensitive data and avoid logging private inputs unnecessarily.",
                        "code": "prediction = model.predict(X_new)\nprint(prediction)",
                        "output": "Displays predictions for X_new after the model has been fitted.",
                        "practice": "List the checks an API should perform before calling a model.",
                        "answer": "Check required fields, data types, valid ranges and missing values, then return controlled errors for invalid input.",
                        "interview": "Inference is the process of using a trained model to produce predictions."
                    }
                ]
            },
            {
                "unit": "Unit 5: Monitoring and Projects",
                "topics": [
                    {
                        "title": "Monitoring and Model Drift",
                        "notes": "Monitor prediction errors, latency, availability and changes in incoming data. Data drift means input distributions change; concept drift means the relationship between inputs and outcomes changes. Monitoring should guide investigation rather than trigger blind automatic retraining.",
                        "code": "metrics = {'latency_ms': 120, 'errors': 2}\nprint(metrics)",
                        "output": "{'latency_ms': 120, 'errors': 2}",
                        "practice": "Identify three measurements to monitor for a prediction API.",
                        "answer": "Latency, error rate and prediction quality are useful measurements.",
                        "interview": "Drift can reduce performance when real-world data changes."
                    },
                    {
                        "title": "Build an ML Project",
                        "notes": "Choose a clear problem, inspect data, build a baseline, create a reproducible pipeline, evaluate the model and document limitations. Compare against simple alternatives. Explain data provenance, metrics and how the model should be used.",
                        "code": "print('Define -> Prepare -> Train -> Evaluate -> Deploy -> Monitor')",
                        "output": "Displays a simplified ML engineering workflow.",
                        "practice": "Prepare a one-page plan for a classification project.",
                        "answer": "Specify the target, features, data source, split strategy, baseline, metrics and intended deployment.",
                        "interview": "A complete ML project includes reliable data preparation and evaluation, not only model training."
                    }
                ]
            }
        ],

        "Data Analyst": [
            {
                "unit": "Unit 1: Spreadsheets and Data Basics",
                "topics": [
                    {
                        "title": "Spreadsheet Formulas",
                        "notes": "Spreadsheets organize information into rows and columns. Learn SUM, AVERAGE, COUNT, IF, sorting, filtering and lookup functions. Use clear headers, consistent data types and separate raw data from analysis.",
                        "code": "=SUM(B2:B10)\n=AVERAGE(B2:B10)",
                        "output": "The formulas calculate the sum and average of cells B2 through B10.",
                        "practice": "Create a marks table and calculate total and average marks.",
                        "answer": "Use SUM for total and AVERAGE for the mean.",
                        "interview": "Spreadsheets support quick calculations and data exploration."
                    },
                    {
                        "title": "Data Quality",
                        "notes": "Check missing values, duplicate records, inconsistent categories and incorrect formats. Keep raw data unchanged and document transformations. Verify totals before and after cleaning.",
                        "code": "import pandas as pd\ndf = pd.read_csv('data.csv')\nprint(df.isnull().sum())",
                        "output": "Shows the number of missing values per column.",
                        "practice": "List three checks you would perform before analysing sales data.",
                        "answer": "Check duplicates, missing values and invalid or inconsistent amounts.",
                        "interview": "Data quality affects the reliability of analysis."
                    }
                ]
            },
            {
                "unit": "Unit 2: SQL",
                "topics": [
                    {
                        "title": "Filtering and Aggregation",
                        "notes": "SELECT retrieves columns, WHERE filters rows and ORDER BY sorts results. GROUP BY creates groups for aggregate calculations. Learn COUNT, SUM, AVG, MIN and MAX. Understand NULL handling and use clear aliases.",
                        "code": "SELECT department, AVG(salary)\nFROM Employees\nGROUP BY department;",
                        "output": "Returns the average salary for each department.",
                        "practice": "Count employees in each department.",
                        "answer": "SELECT department, COUNT(*) FROM Employees GROUP BY department;",
                        "interview": "GROUP BY aggregates records by shared values."
                    },
                    {
                        "title": "Joins and Subqueries",
                        "notes": "Joins combine related tables. INNER JOIN returns matching rows; LEFT JOIN preserves all rows from the left table. Subqueries place a query inside another query. Check join keys and row counts to avoid accidental duplication.",
                        "code": "SELECT s.name, d.department_name\nFROM Students s\nJOIN Departments d\nON s.department_id = d.id;",
                        "output": "Returns student names with matching department names.",
                        "practice": "Explain when you would use LEFT JOIN rather than INNER JOIN.",
                        "answer": "Use LEFT JOIN when every row from the left table must remain, even without a match.",
                        "interview": "A join combines records using a relationship between tables."
                    }
                ]
            },
            {
                "unit": "Unit 3: Python and Statistics",
                "topics": [
                    {
                        "title": "Pandas Analysis",
                        "notes": "Pandas reads tabular data and supports filtering, grouping, aggregation and merging. Inspect data types and summary statistics before calculating results. Keep transformations reproducible and avoid modifying source data unintentionally.",
                        "code": "import pandas as pd\ndf = pd.DataFrame({'sales': [100, 200, 150]})\nprint(df['sales'].sum())",
                        "output": "450",
                        "practice": "Calculate total sales by product category.",
                        "answer": "Group by category and sum the sales column.",
                        "interview": "Pandas makes structured-data analysis convenient."
                    },
                    {
                        "title": "Descriptive Statistics",
                        "notes": "Mean, median and mode describe central tendency. Range, variance and standard deviation describe spread. Percentages help compare groups of different sizes. Correlation measures association but does not by itself establish causation.",
                        "code": "values = [10, 20, 30]\nprint(sum(values) / len(values))",
                        "output": "20.0",
                        "practice": "Explain how an outlier can affect the mean.",
                        "answer": "An extreme value can pull the mean toward itself, while the median is often less affected.",
                        "interview": "Correlation alone does not prove that one variable causes another."
                    }
                ]
            },
            {
                "unit": "Unit 4: Visualization and Dashboards",
                "topics": [
                    {
                        "title": "Choosing Charts",
                        "notes": "Bar charts compare categories; line charts show changes over time; histograms show distributions; scatter plots compare numeric variables. Choose the chart that answers the question and label axes clearly.",
                        "code": "import matplotlib.pyplot as plt\nplt.plot([1, 2, 3], [10, 15, 12])\nplt.xlabel('Month')\nplt.ylabel('Sales')\nplt.show()",
                        "output": "A line chart displays three sales values.",
                        "practice": "Choose a chart for monthly sales across one year.",
                        "answer": "A line chart is a suitable starting point for a monthly time series.",
                        "interview": "Chart selection depends on the data and question."
                    },
                    {
                        "title": "Dashboard Design",
                        "notes": "A dashboard combines key metrics, filters and charts to answer business questions. Put the most important information first, use consistent formatting and avoid unnecessary decoration. Test filters and ensure all figures use clear definitions.",
                        "code": "kpi = {'total_sales': 125000, 'orders': 420}\nprint(kpi)",
                        "output": "Displays two example dashboard metrics.",
                        "practice": "Design three KPIs for a student-performance dashboard.",
                        "answer": "Possible KPIs include average marks, pass percentage and attendance rate, with clearly defined calculations.",
                        "interview": "A dashboard helps users monitor key metrics quickly."
                    }
                ]
            },
            {
                "unit": "Unit 5: Business Insights and Portfolio",
                "topics": [
                    {
                        "title": "Exploratory Analysis",
                        "notes": "Exploratory data analysis examines distributions, relationships, unusual values and patterns. Ask a question before choosing a chart or calculation. Compare groups carefully and verify that differences are meaningful in context.",
                        "code": "print('Question -> Explore -> Validate -> Explain')",
                        "output": "Displays a simplified analysis workflow.",
                        "practice": "Write two questions for a student marks dataset.",
                        "answer": "You could examine subject-wise average marks and compare performance across attendance groups without assuming causation.",
                        "interview": "EDA helps reveal patterns and data-quality problems."
                    },
                    {
                        "title": "Reporting and Portfolio",
                        "notes": "A good report explains the question, method, main findings, limitations and recommendations. Include readable charts and reproducible calculations. A portfolio project should show the data source, cleaning steps, SQL or code, dashboard and conclusions.",
                        "code": "finding = 'Average score increased in the second sample.'\nprint(finding)",
                        "output": "Displays an example observation that would need supporting analysis.",
                        "practice": "Write a short summary for a chart you created.",
                        "answer": "State the measured result, comparison period or groups, and an important limitation.",
                        "interview": "An analyst translates data into useful, evidence-based information."
                    }
                ]
            }
        ],

        "Cybersecurity Analyst": [
            {
                "unit": "Unit 1: Networking Fundamentals",
                "topics": [
                    {
                        "title": "IP, DNS and HTTP",
                        "notes": "An IP address identifies a network interface. DNS translates domain names into records such as IP addresses. HTTP supports web communication, while HTTPS uses TLS to protect data in transit. Understand routers, ports, TCP, UDP and common network services.",
                        "code": "import socket\nprint(socket.gethostname())",
                        "output": "Displays the local machine's hostname.",
                        "practice": "Explain the purpose of DNS and HTTPS.",
                        "answer": "DNS helps resolve domain names; HTTPS protects HTTP traffic using TLS.",
                        "interview": "DNS maps domain names to DNS records, often including IP addresses."
                    },
                    {
                        "title": "Ports and Network Layers",
                        "notes": "Network protocols define communication rules. TCP provides a reliable ordered byte stream; UDP sends datagrams without the same delivery guarantees. Ports identify services on a host. Firewalls apply rules to network traffic.",
                        "code": "services = {'HTTP': 80, 'HTTPS': 443, 'DNS': 53}\nprint(services)",
                        "output": "Displays example conventional service ports.",
                        "practice": "Describe how a browser connects to an HTTPS website.",
                        "answer": "It resolves the hostname, establishes a network connection, negotiates TLS and sends HTTP requests.",
                        "interview": "TCP prioritizes reliable ordered delivery."
                    }
                ]
            },
            {
                "unit": "Unit 2: Operating Systems and Linux",
                "topics": [
                    {
                        "title": "Processes and Permissions",
                        "notes": "An operating system manages processes, memory, files and devices. Users and groups help control access. Apply least privilege: grant only the permissions required for a task. Understand processes, services, logs and file permissions.",
                        "code": "whoami\npwd\nls",
                        "output": "On Linux, these commands display the current user, working directory and directory contents.",
                        "practice": "Explain why administrative access should be limited.",
                        "answer": "Reducing privileged access limits the impact of mistakes and compromised accounts.",
                        "interview": "Least privilege grants only necessary permissions."
                    },
                    {
                        "title": "Linux Logs and Commands",
                        "notes": "Logs record system and application events. Learn safe commands for listing files, inspecting processes and reading permitted logs. Protect confidential log contents. Use timestamps and context to distinguish normal events from suspicious activity.",
                        "code": "date\nwhoami\nps",
                        "output": "Displays date and time, current user and process information on Linux.",
                        "practice": "Explain how timestamps help investigate an event.",
                        "answer": "They help correlate events across logs and establish an approximate sequence.",
                        "interview": "Logs support troubleshooting and incident investigation."
                    }
                ]
            },
            {
                "unit": "Unit 3: Security Fundamentals",
                "topics": [
                    {
                        "title": "CIA Triad and Risk",
                        "notes": "Confidentiality limits data access to authorized users. Integrity protects data from unauthorized alteration. Availability ensures systems and data remain accessible when needed. Risk assessment considers threats, vulnerabilities, likelihood and impact.",
                        "code": "principles = ['Confidentiality', 'Integrity', 'Availability']\nprint(principles)",
                        "output": "Displays the three CIA security principles.",
                        "practice": "Give one example of a control supporting each CIA principle.",
                        "answer": "Access control supports confidentiality, checksums can support integrity, and backups support availability.",
                        "interview": "The CIA triad describes three core information-security goals."
                    },
                    {
                        "title": "Authentication and Access Control",
                        "notes": "Authentication verifies identity. Authorization defines permissions. Multi-factor authentication combines different factor types. Secure systems use unique accounts, strong authentication, limited permissions and protected recovery processes.",
                        "code": "print('Verify identity before granting access')",
                        "output": "Displays a reminder of an authentication principle.",
                        "practice": "Explain the benefit of multi-factor authentication.",
                        "answer": "It adds another factor, making a stolen password alone less likely to be sufficient.",
                        "interview": "Authentication identifies a user; authorization determines allowed actions."
                    }
                ]
            },
            {
                "unit": "Unit 4: Threat Detection and Response",
                "topics": [
                    {
                        "title": "Phishing and Common Threats",
                        "notes": "Phishing attempts to trick users into revealing information or performing unsafe actions. Other risks include malware, weak passwords, misconfiguration and unpatched software. Verify unexpected requests through trusted channels and report suspicious messages according to organizational policy.",
                        "code": "indicators = ['unexpected urgency', 'unfamiliar sender', 'suspicious link']\nprint(indicators)",
                        "output": "Displays example warning signs to investigate.",
                        "practice": "List three warning signs of a suspicious email.",
                        "answer": "Unexpected urgency, mismatched sender details and links to unfamiliar domains are examples.",
                        "interview": "Phishing uses deception to obtain information or trigger unsafe actions."
                    },
                    {
                        "title": "Incident Handling and Logs",
                        "notes": "Incident response commonly includes preparation, detection, analysis, containment, eradication, recovery and lessons learned. Preserve evidence, follow approved procedures and escalate serious incidents to authorized responders. Correlate log events without jumping to unsupported conclusions.",
                        "code": "event = {'type': 'failed_login', 'count': 8}\nprint(event)",
                        "output": "Displays an example security event record.",
                        "practice": "Explain why several failed logins may need investigation.",
                        "answer": "They may indicate user error or suspicious activity; examine context, source, timing and related events before deciding.",
                        "interview": "Incident response aims to contain and recover from security events."
                    }
                ]
            },
            {
                "unit": "Unit 5: Defensive Skills and Career",
                "topics": [
                    {
                        "title": "Vulnerability Management",
                        "notes": "A vulnerability is a weakness that may be exploited. Asset inventory, authorized scanning, risk prioritization and patch management help reduce exposure. Test only systems you own or have explicit permission to assess.",
                        "code": "print('Identify -> Assess -> Prioritize -> Remediate -> Verify')",
                        "output": "Displays a simplified vulnerability-management workflow.",
                        "practice": "Explain why critical updates should be prioritized using risk.",
                        "answer": "Consider severity, exposure, exploitability, asset importance and available mitigations.",
                        "interview": "Vulnerability management reduces risk from known weaknesses."
                    },
                    {
                        "title": "Security Portfolio and Ethics",
                        "notes": "Build a portfolio using safe lab exercises, defensive log analysis and documented learning. Never test real systems without authorization. Explain your findings, evidence and limitations. Study networking, Linux, scripting, security fundamentals and incident response.",
                        "code": "print('Learn ethically. Test with permission. Document evidence.')",
                        "output": "Displays basic professional security principles.",
                        "practice": "Plan a defensive lab that analyses sample login logs.",
                        "answer": "Use synthetic or authorized logs, identify patterns and document findings without exposing private data.",
                        "interview": "Authorization and responsible handling of evidence are essential in security work."
                    }
                ]
            }
        ],

        "Cloud / DevOps Engineer": [
            {
                "unit": "Unit 1: Linux and Networking",
                "topics": [
                    {
                        "title": "Linux Fundamentals",
                        "notes": "Linux is widely used on servers. Learn navigation, file operations, permissions, processes, services, environment variables and logs. Use commands carefully, especially those that modify or delete files. Understand users, groups and least privilege.",
                        "code": "pwd\nls\nwhoami",
                        "output": "Displays the current directory, directory contents and current user on Linux.",
                        "practice": "Explain the purpose of the current-directory and list commands.",
                        "answer": "pwd shows the working directory; ls lists directory contents.",
                        "interview": "Linux is common in server and cloud environments."
                    },
                    {
                        "title": "Networking and DNS",
                        "notes": "Cloud systems rely on IP addresses, DNS, routing, ports, firewalls and secure protocols. Understand how clients connect to services and how network rules limit access. Diagnose connectivity systematically rather than changing many settings at once.",
                        "code": "services = {'HTTP': 80, 'HTTPS': 443}\nprint(services)",
                        "output": "Displays example HTTP and HTTPS port numbers.",
                        "practice": "Explain why a server can be running but still unreachable.",
                        "answer": "Possible causes include firewall rules, routing, DNS, port binding or service configuration.",
                        "interview": "DNS resolves names to records used to locate services."
                    }
                ]
            },
            {
                "unit": "Unit 2: Git and Scripting",
                "topics": [
                    {
                        "title": "Git Workflow",
                        "notes": "Git tracks changes, commits snapshots and supports branches. Use meaningful commit messages and review status before committing. Remote repositories enable collaboration. Resolve conflicts carefully and avoid committing credentials or generated secrets.",
                        "code": "git status\ngit add .\ngit commit -m \"Update application\"",
                        "output": "Checks repository status, stages changes and records a commit.",
                        "practice": "Explain why branches are useful when developing a feature.",
                        "answer": "Branches isolate work so changes can be reviewed and merged separately.",
                        "interview": "Version control records project history and supports collaboration."
                    },
                    {
                        "title": "Shell and Python Automation",
                        "notes": "Scripting automates repetitive tasks. Shell scripts combine commands; Python scripts can process files, call APIs and transform data. Add input validation, useful logs and safe failure handling. Avoid destructive automation without checks.",
                        "code": "for name in ['app', 'database', 'tests']:\n    print('Checking', name)",
                        "output": "Prints a check message for each listed component.",
                        "practice": "Describe a repetitive task that could be safely automated.",
                        "answer": "For example, a script can validate required files before a deployment begins.",
                        "interview": "Automation improves repeatability and reduces manual work."
                    }
                ]
            },
            {
                "unit": "Unit 3: Cloud Fundamentals",
                "topics": [
                    {
                        "title": "Cloud Service Models",
                        "notes": "IaaS provides infrastructure resources; PaaS provides a managed platform for applications; SaaS provides ready-to-use software. Public, private and hybrid cloud describe different deployment approaches. Choose services based on requirements, security, cost and operational needs.",
                        "code": "models = ['IaaS', 'PaaS', 'SaaS']\nprint(models)",
                        "output": "Displays the three common cloud service models.",
                        "practice": "Classify a hosted application platform by its service model and explain why.",
                        "answer": "A managed application platform is commonly PaaS, though exact responsibilities depend on the provider.",
                        "interview": "The service models differ in how much infrastructure the provider manages."
                    },
                    {
                        "title": "Storage, Compute and IAM",
                        "notes": "Compute runs workloads, storage keeps data and networking connects services. Identity and Access Management controls permissions. Apply least privilege, secure credentials and monitor usage. Learn that cloud resources can incur costs even when not actively used.",
                        "code": "print('Compute + Storage + Network + Access Control')",
                        "output": "Displays basic cloud building blocks.",
                        "practice": "Explain why a cloud user should receive only necessary permissions.",
                        "answer": "It limits accidental changes and reduces the potential impact of compromised credentials.",
                        "interview": "IAM controls identities and their permitted actions."
                    }
                ]
            },
            {
                "unit": "Unit 4: CI/CD and Containers",
                "topics": [
                    {
                        "title": "Continuous Integration and Delivery",
                        "notes": "Continuous Integration regularly combines code changes and runs automated checks. Continuous Delivery keeps changes ready for release; Continuous Deployment automatically releases qualifying changes. Pipelines may run tests, build artifacts and deploy approved versions.",
                        "code": "print('Commit -> Test -> Build -> Deploy')",
                        "output": "Displays a simplified CI/CD pipeline.",
                        "practice": "List three checks a pipeline should run before deployment.",
                        "answer": "Run automated tests, verify dependencies and check build success.",
                        "interview": "CI/CD automates repeatable validation and release workflows."
                    },
                    {
                        "title": "Containers and Images",
                        "notes": "A container packages an application with its dependencies into an isolated runtime environment. An image is the template used to create containers. Containers can improve consistency but still require secure configuration, updates, resource limits and monitoring.",
                        "code": "docker build -t my-app .\ndocker run --rm my-app",
                        "output": "Builds an image and runs a container, assuming a valid Dockerfile and installed Docker.",
                        "practice": "Explain the difference between an image and a running container.",
                        "answer": "An image is a packaged template; a container is a running or created instance of that image.",
                        "interview": "Containers help package and run applications consistently."
                    }
                ]
            },
            {
                "unit": "Unit 5: Monitoring and Deployment Projects",
                "topics": [
                    {
                        "title": "Logs, Metrics and Reliability",
                        "notes": "Logs record events, metrics measure numeric behaviour and traces help follow requests across services. Monitor availability, latency, error rate and resource use. Alerts should be actionable and tested. Backups and recovery procedures support resilience.",
                        "code": "health = {'status': 'ok', 'latency_ms': 85}\nprint(health)",
                        "output": "Displays example application health information.",
                        "practice": "Choose three useful monitoring metrics for a web application.",
                        "answer": "Availability, request latency and error rate are useful starting metrics.",
                        "interview": "Monitoring helps detect failures and performance degradation."
                    },
                    {
                        "title": "Deployment Project and Cost Control",
                        "notes": "Deploy a small application with documented configuration, a health check and logs. Use environment variables for secrets. Review permissions, storage, resource usage and billing settings. Delete unneeded resources and set budget alerts where supported.",
                        "code": "print('Build -> Configure -> Deploy -> Verify -> Monitor')",
                        "output": "Displays a simplified deployment workflow.",
                        "practice": "Prepare a deployment checklist for a student web application.",
                        "answer": "Check dependencies, secrets, access rules, health endpoint, logs, URL and cost controls.",
                        "interview": "Reliable deployment requires configuration, verification and ongoing monitoring."
                    }
                ]
            }
        ]
    }

    # ---------------------------------------------------------
    # COURSE SELECTION
    # ---------------------------------------------------------

    career_names = list(courses.keys())

    saved_goal = database.get_career_goal(
        st.session_state["user_id"]
    )

    if saved_goal in career_names:
        default_index = career_names.index(saved_goal)
    else:
        default_index = 0

    selected_career = st.selectbox(
        "🎯 Select your career course",
        career_names,
        index=default_index,
        key="learning_hub_career"
    )

    selected_units = courses[selected_career]

    st.subheader(f"📖 {selected_career}")
    st.caption(
        "Choose a unit below to study the theory, examples, "
        "practice exercises and interview questions."
    )

    # ---------------------------------------------------------
    # PROGRESS CHECKLIST
    # ---------------------------------------------------------

    st.subheader("✅ My Learning Progress")

    progress_items = []
    for unit in selected_units:
        for topic in unit["topics"]:
            progress_items.append(
                f'{unit["unit"]} - {topic["title"]}'
            )

    progress_key = (
        "learning_progress_"
        + selected_career.replace("/", "_").replace(" ", "_")
    )

    if progress_key not in st.session_state:
        st.session_state[progress_key] = []

    completed_items = st.session_state[progress_key]

    completed_count = sum(
        1 for item in progress_items
        if item in completed_items
    )

    progress_value = (
        completed_count / len(progress_items)
        if progress_items else 0
    )

    st.progress(progress_value)
    st.write(
        f"Completed: {completed_count} of "
        f"{len(progress_items)} topics "
        f"({int(progress_value * 100)}%)"
    )

    with st.expander("Update your topic checklist"):
        updated_completed = []
        for item in progress_items:
            is_checked = st.checkbox(
                item,
                value=item in completed_items,
                key=f"check_{progress_key}_{item}"
            )
            if is_checked:
                updated_completed.append(item)

        st.session_state[progress_key] = updated_completed

        if st.button(
            "Refresh Progress",
            key=f"refresh_{progress_key}"
        ):
            st.rerun()

    st.caption(
        "Progress is currently stored in this Streamlit session. "
        "It may reset when the session restarts."
    )

    # ---------------------------------------------------------
    # READ NOTES ON THE PAGE
    # ---------------------------------------------------------

    st.divider()
    st.subheader("📚 Unit-wise Study Notes")

    for unit_index, unit in enumerate(selected_units):
        with st.expander(unit["unit"], expanded=(unit_index == 0)):
            for topic in unit["topics"]:
                st.markdown(f"### {topic['title']}")
                st.markdown(topic["notes"])

                if topic.get("code"):
                    st.markdown("**Example Code**")
                    st.code(topic["code"], language="python")

                if topic.get("output"):
                    st.markdown("**Expected Output / Result**")
                    st.code(topic["output"], language="text")

                st.markdown("**Practice Exercise**")
                st.write(topic["practice"])

                st.markdown("**Solution / Suggested Answer**")
                st.code(topic["answer"], language="python")

                st.markdown("**Interview Question**")
                st.write(topic["interview"])
                st.divider()

    # ---------------------------------------------------------
    # PDF GENERATOR
    # ---------------------------------------------------------
    
    def create_course_pdf(course_name, units):
        import io
        from xml.sax.saxutils import escape

        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import (
            getSampleStyleSheet,
            ParagraphStyle,
        )
        from reportlab.lib.units import inch
        from reportlab.platypus import (
            SimpleDocTemplate,
            Paragraph,
            Spacer,
            PageBreak,
            Preformatted,
            KeepTogether,
        )

        buffer = io.BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=0.65 * inch,
            leftMargin=0.65 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.65 * inch,
            title=f"{course_name} - Learning Guide",
            author="SkillPath AI",
        )

        styles = getSampleStyleSheet()

        styles.add(ParagraphStyle(
            name="CoverTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=25,
            leading=32,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#17365D"),
            spaceAfter=20,
        ))

        styles.add(ParagraphStyle(
            name="CoverSubtitle",
            parent=styles["Normal"],
            fontSize=12,
            leading=19,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#526579"),
        ))

        styles.add(ParagraphStyle(
            name="UnitHeading",
            parent=styles["Heading1"],
            fontSize=17,
            leading=22,
            textColor=colors.HexColor("#17365D"),
            spaceBefore=10,
            spaceAfter=12,
            keepWithNext=True,
        ))

        styles.add(ParagraphStyle(
            name="TopicHeading",
            parent=styles["Heading2"],
            fontSize=13,
            leading=17,
            textColor=colors.HexColor("#176B87"),
            spaceBefore=12,
            spaceAfter=6,
            keepWithNext=True,
        ))

        styles.add(ParagraphStyle(
            name="BodyTextCustom",
            parent=styles["BodyText"],
            fontSize=9.5,
            leading=14,
            spaceAfter=7,
            splitLongWords=True,
        ))

        styles.add(ParagraphStyle(
            name="SectionLabel",
            parent=styles["Heading3"],
            fontSize=10,
            leading=13,
            textColor=colors.HexColor("#34495E"),
            spaceBefore=7,
            spaceAfter=4,
            keepWithNext=True,
        ))

        styles.add(ParagraphStyle(
            name="CodeCustom",
            fontName="Courier",
            fontSize=8,
            leading=11,
            leftIndent=8,
            rightIndent=8,
            borderColor=colors.HexColor("#D6DEE8"),
            borderWidth=0.5,
            borderPadding=7,
            backColor=colors.HexColor("#F3F6FA"),
            spaceBefore=4,
            spaceAfter=8,
        ))

        story = []

        # Cover page
        story.append(Spacer(1, 1.5 * inch))
        story.append(Paragraph(
            "SkillPath AI",
            styles["CoverTitle"]
        ))
        story.append(Paragraph(
            escape(str(course_name)) + "<br/><br/>"
            "Career Learning Guide<br/>"
            "English Study Notes | Examples | Practice | Interview Preparation",
            styles["CoverSubtitle"]
        ))
        story.append(Spacer(1, 1.0 * inch))
        story.append(Paragraph(
            "A structured learning resource for students and beginners.",
            styles["BodyTextCustom"]
        ))
        story.append(PageBreak())

        
        # Normalize course data for PDF rendering
        normalized_units = []

        if isinstance(units, dict):
            raw_units = list(units.items())
        else:
            raw_units = []

            for i, unit in enumerate(units):
                if isinstance(unit, dict) and "topics" in unit:
                    unit_name = (
                        unit.get("title")
                        or unit.get("unit")
                        or unit.get("name")
                        or f"Unit {i + 1}"
                    )
                    raw_units.append((unit_name, unit["topics"]))
                else:
                    raw_units.append((f"Unit {i + 1}", unit))

        for unit_name, topics in raw_units:
            topic_items = []

            if isinstance(topics, dict):
                # A single topic dictionary
                if any(k in topics for k in ("notes", "code", "practice")):
                    topic_items.append((
                        topics.get("title", "Topic"),
                        topics
                    ))
                else:
                    topic_items = list(topics.items())

            elif isinstance(topics, list):
                for j, topic in enumerate(topics):
                    if isinstance(topic, dict):
                        topic_title = (
                            topic.get("title")
                            or topic.get("name")
                            or f"Topic {j + 1}"
                        )
                        topic_items.append((topic_title, topic))
                    else:
                        topic_items.append((f"Topic {j + 1}", topic))

            else:
                topic_items.append(("Overview", topics))

            normalized_units.append((unit_name, topic_items))

        # Contents page
        story.append(Paragraph("Contents", styles["UnitHeading"]))

        for unit_name, topic_items in normalized_units:
            story.append(Paragraph(
                escape(str(unit_name)),
                styles["BodyTextCustom"]
            ))

            for topic_name, content in topic_items:
                story.append(Paragraph(
                    "&nbsp;&nbsp;&nbsp;&nbsp;&#8226; "
                    + escape(str(topic_name)),
                    styles["BodyTextCustom"]
                ))

        story.append(PageBreak())

        def add_learning_sections(story, topic_name, content, styles):
            """Add revision material to a topic without duplicating long notes."""
            story.append(Paragraph(
                "Learning Objectives",
                styles["SectionLabel"]
            ))
            story.append(Paragraph(
                "After studying this topic, you should be able to explain "
                + escape(str(topic_name))
                + ", identify its key ideas, and apply them to a practical problem.",
                styles["BodyTextCustom"]
            ))

            story.append(Paragraph(
                "Practical Applications",
                styles["SectionLabel"]
            ))
            story.append(Paragraph(
                "Relate this concept to a small project or a real software task. "
                "Consider when it is useful, what problem it solves, and what "
                "limitations or common mistakes should be considered.",
                styles["BodyTextCustom"]
            ))

            story.append(Paragraph(
                "Revision Questions",
                styles["SectionLabel"]
            ))
            questions = [
                "Define " + str(topic_name) + ".",
                "Explain its important concepts in your own words.",
                "Describe one practical application.",
                "What common mistakes should a beginner avoid?",
                "How would you explain this topic in a technical interview?"
            ]
            for question in questions:
                story.append(Paragraph(
                    "&#8226; " + escape(question),
                    styles["BodyTextCustom"]
                ))

        # Render all units and topics inside create_course_pdf.
        topic_number = 0
        for unit_name, topic_items in normalized_units:
            story.append(Paragraph(
                escape(str(unit_name)),
                styles["UnitHeading"]
            ))

            for topic_name, content in topic_items:
                # Start each topic on a fresh page to make the PDF read
                # like a textbook and ensure enough pages for the full course.
                # The first topic follows the contents page directly.
                if topic_number > 0:
                    story.append(PageBreak())
                topic_number += 1

                story.append(Paragraph(
                    escape(str(topic_name)),
                    styles["TopicHeading"]
                ))

                if isinstance(content, dict):
                    # Keep the most useful course fields in a readable order.
                    preferred_order = [
                        "notes", "code", "output", "practice",
                        "answer", "interview"
                    ]
                    labels = list(content.keys())
                    labels.sort(
                        key=lambda label: (
                            preferred_order.index(str(label).lower())
                            if str(label).lower() in preferred_order
                            else len(preferred_order)
                        )
                    )

                    second_page_started = False
                    for label in labels:
                        if label in ("title", "name", "unit", "topics"):
                            continue
                        value = content[label]
                        if value is None or value == "":
                            continue

                        label_lower = str(label).lower()
                        if (
                            label_lower in ("practice", "answer", "interview")
                            and not second_page_started
                        ):
                            story.append(PageBreak())
                            second_page_started = True

                        display_label = str(label).replace("_", " ").title()
                        story.append(Paragraph(
                            escape(display_label),
                            styles["SectionLabel"]
                        ))

                        if isinstance(value, (list, tuple)):
                            for item in value:
                                story.append(Paragraph(
                                    "&#8226; " + escape(str(item)),
                                    styles["BodyTextCustom"]
                                ))
                        elif label_lower in (
                            "code", "program", "python code", "java code",
                            "example code", "answer", "output",
                            "sample output", "expected output"
                        ):
                            story.append(Preformatted(
                                str(value).expandtabs(4),
                                styles["CodeCustom"],
                                maxLineLength=100,
                                dedent=0,
                            ))
                        else:
                            safe_text = escape(str(value)).replace(
                                "\\n", "<br/>"
                            )
                            story.append(Paragraph(
                                safe_text,
                                styles["BodyTextCustom"]
                            ))
                else:
                    safe_text = escape(str(content)).replace(
                        "\\n", "<br/>"
                    )
                    story.append(Paragraph(
                        safe_text,
                        styles["BodyTextCustom"]
                    ))

                if isinstance(content, dict) and not second_page_started:
                    story.append(PageBreak())
                elif not isinstance(content, dict):
                    story.append(PageBreak())

                add_learning_sections(story, topic_name, content, styles)
                story.append(Spacer(1, 8))

        if topic_number == 0:
            story.append(Paragraph(
                "No course topics were available to include in this PDF.",
                styles["BodyTextCustom"]
            ))

        # Repeating footer and page numbers.
        def add_page_number(canvas, document):
            canvas.saveState()
            page_number = canvas.getPageNumber()
            if page_number > 1:
                canvas.setFont("Helvetica", 8)
                canvas.setFillColor(colors.HexColor("#65758B"))
                canvas.drawString(
                    0.65 * inch,
                    0.38 * inch,
                    "SkillPath AI | " + str(course_name)
                )
                canvas.drawRightString(
                    A4[0] - 0.65 * inch,
                    0.38 * inch,
                    f"Page {page_number}"
                )
            canvas.restoreState()

        doc.build(
            story,
            onFirstPage=add_page_number,
            onLaterPages=add_page_number,
        )
        pdf_bytes = buffer.getvalue()
        buffer.close()

        if not pdf_bytes.startswith(b"%PDF"):
            raise RuntimeError("PDF generation did not produce a valid PDF file.")
        return pdf_bytes

    # ---------------------------------------------------------
    # DOWNLOAD PDF
    # ---------------------------------------------------------

    st.divider()
    st.subheader("⬇️ Download Course PDF")

    st.write(
        "Download the selected career's notes as a PDF "
        "for offline reading and revision."
    )

    try:
        pdf_data = create_course_pdf(
            selected_career,
            selected_units
        )
        if not isinstance(pdf_data, (bytes, bytearray)) or not pdf_data:
            raise RuntimeError("PDF generator returned empty or invalid data.")

        safe_filename = (
            selected_career.lower()
            .replace("/", "_")
            .replace(" ", "_")
        )

        st.download_button(
            label="📥 Download Complete Course PDF",
            data=pdf_data,
            file_name=f"{safe_filename}_complete_notes.pdf",
            mime="application/pdf",
            key=f"download_{safe_filename}"
        )

        st.success(
            "Your course PDF is ready. "
            "Select the download button to save it."
        )

    except Exception as error:
        st.error("Unable to generate the PDF.")
        st.exception(error)

    # ---------------------------------------------------------
    # FREE LEARNING RESOURCES
    # ---------------------------------------------------------

    st.divider()
    st.subheader("🌐 Free Learning Resources")

    resource_map = {
        "Software Developer": [
            ("Python Official Tutorial", "https://docs.python.org/3/tutorial/"),
            ("HackerRank Practice", "https://www.hackerrank.com/domains/python"),
            ("GitHub Skills", "https://skills.github.com/")
        ],
        "Web Developer": [
            ("W3Schools", "https://www.w3schools.com/"),
            ("MDN Web Docs", "https://developer.mozilla.org/"),
            ("freeCodeCamp", "https://www.freecodecamp.org/")
        ],
        "Data Scientist": [
            ("Pandas Documentation", "https://pandas.pydata.org/docs/"),
            ("Kaggle Learn", "https://www.kaggle.com/learn"),
            ("Google Colab", "https://colab.research.google.com/")
        ],
        "Machine Learning Engineer": [
            ("Scikit-learn Tutorials", "https://scikit-learn.org/stable/tutorial/"),
            ("Google ML Crash Course", "https://developers.google.com/machine-learning/crash-course"),
            ("Kaggle Learn", "https://www.kaggle.com/learn")
        ],
        "Data Analyst": [
            ("SQLBolt", "https://sqlbolt.com/"),
            ("Kaggle Learn", "https://www.kaggle.com/learn"),
            ("Pandas Documentation", "https://pandas.pydata.org/docs/")
        ],
        "Cybersecurity Analyst": [
            ("Cisco Networking Academy", "https://www.netacad.com/"),
            ("OverTheWire Wargames", "https://overthewire.org/wargames/"),
            ("Linux Journey", "https://linuxjourney.com/")
        ],
        "Cloud / DevOps Engineer": [
            ("Docker Get Started", "https://docs.docker.com/get-started/"),
            ("GitHub Skills", "https://skills.github.com/"),
            ("Microsoft Learn", "https://learn.microsoft.com/training/")
        ]
    }

    for resource_name, resource_url in resource_map[selected_career]:
        st.markdown(f"- [{resource_name}]({resource_url})")

    st.caption(
        "These notes are educational study material. "
        "Verify commands and concepts against official documentation "
        "before using them in production projects."
    )




# =========================================================
# JOBS & INTERNSHIPS
# =========================================================


elif page == "Jobs & Internships":
    st.header("💼 Jobs & Internships")
    st.write(
        "Search current job and internship listings using the Jooble API. "
        "Listings come from the job provider, not from hard-coded sample vacancies. "
        "Always verify a listing before applying."
    )

    career_options = [
        "Software Developer",
        "Web Developer",
        "Data Scientist",
        "Machine Learning Engineer",
        "Data Analyst",
        "Cybersecurity Analyst",
        "Cloud / DevOps Engineer",
    ]

    saved_goal = database.get_career_goal(st.session_state.user_id)

    if saved_goal in career_options:
        default_career_index = career_options.index(saved_goal)
    else:
        default_career_index = 0
        st.info(
            "Tip: save your preferred career on the Career Goals page "
            "to preselect it here."
        )

    st.subheader("🔎 Find matching opportunities")

    filter_col1, filter_col2 = st.columns(2)

    with filter_col1:
        target_career = st.selectbox(
            "Career track",
            career_options,
            index=default_career_index,
            key="jobs_target_career",
        )

        opportunity_type = st.selectbox(
            "Opportunity type",
            ["Internships", "Entry-level jobs", "Both"],
            key="jobs_opportunity_type",
        )

        location = st.text_input(
            "Preferred location",
            value="Bengaluru",
            help="Enter a city such as Bengaluru or Hyderabad. Use India for country-wide search.",
            key="jobs_location",
        ).strip()

    with filter_col2:
        work_mode = st.selectbox(
            "Work mode",
            ["Any work mode", "Remote", "Hybrid", "On-site"],
            key="jobs_work_mode",
        )

        paid_only = st.checkbox(
            "Prefer listings that mention pay or stipend",
            value=True,
            key="jobs_paid_only",
        )

        beginner_friendly = st.checkbox(
            "Prioritize intern / junior / fresher roles",
            value=True,
            key="jobs_beginner_friendly",
        )

    search_terms = {
        "Software Developer": "software developer",
        "Web Developer": "web developer",
        "Data Scientist": "data scientist",
        "Machine Learning Engineer": "machine learning engineer",
        "Data Analyst": "data analyst",
        "Cybersecurity Analyst": "cybersecurity analyst",
        "Cloud / DevOps Engineer": "cloud devops engineer",
    }

    base_keywords = search_terms[target_career]

    if opportunity_type == "Internships":
        query_keywords = f"{base_keywords} internship"
    elif opportunity_type == "Entry-level jobs":
        query_keywords = f"{base_keywords} fresher junior entry level"
    else:
        query_keywords = base_keywords

    if work_mode == "Remote":
        query_keywords += " remote"
    elif work_mode == "Hybrid":
        query_keywords += " hybrid"

    chosen_location = location or "India"

    encoded_keywords = quote_plus(query_keywords)
    encoded_location = quote_plus(chosen_location)

    st.caption(
        f"Search: {query_keywords} · Location: {chosen_location}. "
        "Listings are supplied by Jooble and may change."
    )

    # Read the Jooble API key from the project's .env file.
    load_dotenv()
    jooble_api_key = os.getenv("JOOBLE_API_KEY", "").strip()

    @st.cache_data(ttl=3600, show_spinner=False)
    def fetch_jooble_jobs(api_key, keywords, location):
        """Fetch provider-supplied job listings from Jooble."""
        endpoint = f"https://in.jooble.org/api/{api_key}"

        payload = {
            "keywords": keywords,
            "location": location,
            "page": 1,
            "ResultOnPage": 20,
            "companysearch": False,
        }

        response = requests.post(
            endpoint,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=20,
        )
        response.raise_for_status()

        data = response.json()
        return data.get("jobs", [])

    st.divider()
    st.subheader("📌 Matching listings")

    if not jooble_api_key:
        st.warning(
            "Live listings are not connected yet. "
            "No sample or invented job cards will be displayed."
        )
        st.markdown("**Set up the API (one time):**")
        st.markdown(
            "1. Obtain your API key from the Jooble API portal.\n"
            "2. Open the `.env` file in your SkillPath-AI project folder.\n"
            "3. Add the following line with your actual key:"
        )
        st.code(
            "JOOBLE_API_KEY=your_actual_jooble_api_key",
            language="text",
        )
        st.caption(
            "Keep the .env file private. Never upload your API key to GitHub. "
            "Restart Streamlit after changing the key."
        )

    else:
        try:
            with st.spinner("Searching current Jooble listings..."):
                job_results = fetch_jooble_jobs(
                    jooble_api_key,
                    query_keywords,
                    chosen_location,
                )

            # Jooble returns location, company, snippet and other fields as strings.
            def job_text(job):
                return " ".join(
                    str(job.get(field) or "")
                    for field in ("title", "snippet", "location", "type")
                ).lower()

            # Filter work mode using the text actually supplied by the provider.
            if work_mode == "Remote":
                job_results = [
                    job for job in job_results
                    if "remote" in job_text(job)
                ]
            elif work_mode == "Hybrid":
                job_results = [
                    job for job in job_results
                    if "hybrid" in job_text(job)
                ]
            elif work_mode == "On-site":
                job_results = [
                    job for job in job_results
                    if not any(
                        word in job_text(job)
                        for word in ("remote", "work from home", "hybrid")
                    )
                ]

            # Filter internships and entry-level jobs.
            if opportunity_type == "Internships":
                job_results = [
                    job for job in job_results
                    if any(
                        word in job_text(job)
                        for word in (
                            "intern", "internship", "internships", "trainee"
                        )
                    )
                ]
            elif opportunity_type == "Entry-level jobs":
                job_results = [
                    job for job in job_results
                    if any(
                        word in job_text(job)
                        for word in (
                            "fresher", "junior", "entry level", "entry-level",
                            "graduate", "associate", "trainee"
                        )
                    )
                ]

            # Prioritize listings that mention a salary or stipend.
            if paid_only:
                def mentions_pay(job):
                    text = (
                        str(job.get("title") or "") + " "
                        + str(job.get("snippet") or "") + " "
                        + str(job.get("salary") or "")
                    ).lower()

                    return bool(str(job.get("salary") or "").strip()) or any(
                        term in text
                        for term in (
                            "stipend", "paid internship", "paid intern",
                            "salary", "₹", "inr", "per month"
                        )
                    )

                job_results = sorted(
                    job_results,
                    key=mentions_pay,
                    reverse=True,
                )

            # Prioritize fresher-friendly roles without inventing listings.
            if beginner_friendly:
                beginner_words = (
                    "intern", "junior", "fresher", "entry-level",
                    "entry level", "graduate", "trainee", "associate"
                )
                job_results = sorted(
                    job_results,
                    key=lambda job: any(
                        word in job_text(job)
                        for word in beginner_words
                    ),
                    reverse=True,
                )

            if not job_results:
                st.info(
                    "No listings matched the selected filters in this "
                    "Jooble response. Try another location, select 'Both', "
                    "or relax the filters. No placeholder jobs are shown."
                )

            else:
                st.success(
                    f"Found {len(job_results)} matching listing(s) from Jooble."
                )

                for job in job_results:
                    job_title = str(
                        job.get("title") or "Untitled listing"
                    )
                    company_name = str(
                        job.get("company") or "Company not specified"
                    )
                    job_location = str(
                        job.get("location") or "Location not specified"
                    )
                    description = str(
                        job.get("snippet")
                        or "No description snippet supplied by the provider."
                    )
                    apply_url = str(job.get("link") or "")
                    updated = str(
                        job.get("updated") or "Date not provided"
                    )
                    pay_text = str(
                        job.get("salary") or "Pay / stipend not stated"
                    )
                    job_type = str(
                        job.get("type") or "Not specified"
                    )

                    with st.container(border=True):
                        title_col, date_col = st.columns([4, 2])

                        with title_col:
                            st.markdown(f"### {job_title}")
                            st.write(f"**{company_name}**")

                        with date_col:
                            st.caption(f"Updated: {updated}")
                            st.caption(f"Location: {job_location}")

                        meta_col1, meta_col2 = st.columns(2)

                        with meta_col1:
                            st.write(f"**Pay:** {pay_text}")

                        with meta_col2:
                            st.write(f"**Type:** {job_type}")

                        with st.expander("Listing description"):
                            st.write(description)

                        if apply_url.startswith("https://"):
                            st.markdown(
                                f"[View original listing / apply]({apply_url})"
                            )
                        else:
                            st.caption(
                                "The provider did not return a valid HTTPS "
                                "application link for this listing."
                            )

                        st.caption(
                            f"Source: {job.get('source') or 'Jooble'} · "
                            "Verify the vacancy before applying."
                        )

        except requests.exceptions.Timeout:
            st.error(
                "Jooble took too long to respond. Please try again later."
            )

        except requests.exceptions.HTTPError as exc:
            status_code = (
                exc.response.status_code
                if exc.response is not None
                else "unknown"
            )

            if status_code == 403:
                st.error(
                    "Jooble rejected the API key (HTTP 403). "
                    "Check that the key is correct and active."
                )
            elif status_code == 404:
                st.error(
                    "Jooble API endpoint was not found (HTTP 404). "
                    "Check the API endpoint and regional key."
                )
            else:
                st.error(
                    f"Jooble returned HTTP {status_code}. "
                    "Please check API access and try again."
                )

        except (requests.exceptions.RequestException, ValueError) as exc:
            st.error(
                "Could not load Jooble listings. "
                f"Check your internet connection and try again. Details: {exc}"
            )

        except Exception as exc:
            st.error(
                f"Unexpected error while loading job listings: {exc}"
            )

    with st.expander("More job-search platforms"):
        st.markdown(
            "- [Search on Internshala](https://internshala.com/internships/)\n"
            "- [Open AICTE Internship Portal](https://internship.aicte-india.org/)\n"
            f"- [Search internships on LinkedIn](https://www.linkedin.com/jobs/search/?keywords={encoded_keywords}&location={encoded_location})\n"
            f"- [Search jobs on Indeed India](https://in.indeed.com/jobs?q={encoded_keywords}&l={encoded_location})\n"
            "- [National Career Service (Government of India)](https://www.ncs.gov.in/)"
        )

    st.divider()
    st.subheader("✅ Before you apply")

    checklist_col1, checklist_col2 = st.columns(2)

    with checklist_col1:
        st.markdown(
            "**Prepare your application**\n"
            "- Keep a one-page student resume ready.\n"
            "- Add 1–3 projects with working links.\n"
            "- List only skills you can explain honestly.\n"
            "- Include GitHub or portfolio links if available."
        )

    with checklist_col2:
        st.markdown(
            "**Check the opportunity**\n"
            "- Read eligibility, dates and work-mode details.\n"
            "- Confirm the role on the company's official website.\n"
            "- Never pay a registration or interview fee to get a job.\n"
            "- Never share OTPs, passwords or banking PINs."
        )

    st.caption(
        "Listings are supplied by a third-party job search API. "
        "SkillPath AI cannot guarantee that every vacancy is still open, "
        "genuine, or suitable. Verify the employer before sharing "
        "personal information."
    )



# =========================================================
# AI RESUME ANALYZER
# =========================================================

elif page == "AI Resume Analyzer":
    import re
    from pypdf import PdfReader

    st.header("📄 AI Resume Analyzer")
    st.write(
        "Upload your resume to review its skills, projects, "
        "education, career alignment and improvement areas."
    )

    st.info(
        "Privacy: this version analyzes extracted PDF text locally "
        "inside your app. It does not send your resume to an AI API."
    )

    # Get the student's saved career goal
    saved_goal = database.get_career_goal(st.session_state.user_id)

    if saved_goal:
        st.write(f"**Your saved career goal:** {saved_goal}")
    else:
        st.warning(
            "You have not saved a career goal yet. "
            "You can still analyze your resume."
        )

    uploaded_resume = st.file_uploader(
        "Upload your resume (PDF only)",
        type=["pdf"],
        key="resume_analyzer_upload"
    )

    job_description = st.text_area(
        "Optional: Paste a job description to compare",
        placeholder="Paste the job requirements here...",
        height=150,
        key="resume_job_description"
    )

    if st.button(
        "🔍 Analyze My Resume",
        type="primary",
        use_container_width=True
    ):
        if uploaded_resume is None:
            st.warning("Please upload your resume PDF first.")

        else:
            try:
                reader = PdfReader(uploaded_resume)

                if reader.is_encrypted:
                    st.error(
                        "This PDF is password-protected. "
                        "Please upload an accessible PDF."
                    )
                    st.stop()

                resume_text = "\n".join(
                    page.extract_text() or ""
                    for page in reader.pages
                )

                if not resume_text.strip():
                    st.error(
                        "No readable text was found. "
                        "This may be a scanned PDF. "
                        "Please try a text-based PDF."
                    )
                    st.stop()

                resume_lower = resume_text.lower()

                # Common skills for a beginner's resume review
                skill_groups = {
                    "Programming": [
                        "python", "java", "c++", "c programming",
                        "javascript", "sql"
                    ],
                    "Web Development": [
                        "html", "css", "react", "node.js",
                        "flask", "django"
                    ],
                    "Data Science and AI": [
                        "pandas", "numpy", "machine learning",
                        "data analysis", "data visualization",
                        "scikit-learn", "tensorflow"
                    ],
                    "Tools": [
                        "git", "github", "excel", "power bi",
                        "tableau", "streamlit"
                    ],
                    "Core Computer Science": [
                        "data structures", "algorithms",
                        "object-oriented programming", "dbms",
                        "operating systems", "computer networks"
                    ]
                }

                found_skills = []

                for group, skills in skill_groups.items():
                    group_found = []

                    for skill in skills:
                        pattern = (
                            r"(?<![a-z0-9+#])"
                            + re.escape(skill)
                            + r"(?![a-z0-9+#])"
                        )

                        if re.search(pattern, resume_lower):
                            group_found.append(skill)

                    if group_found:
                        found_skills.extend(group_found)

                # Career-specific starter skill checklist
                career_skills = {
                    "Software Developer": [
                        "python", "java", "data structures",
                        "algorithms", "sql", "git"
                    ],
                    "Web Developer": [
                        "html", "css", "javascript",
                        "react", "git", "sql"
                    ],
                    "Data Scientist": [
                        "python", "pandas", "numpy",
                        "statistics", "machine learning", "sql"
                    ],
                    "Data Analyst": [
                        "sql", "excel", "python", "pandas",
                        "data analysis", "power bi"
                    ],
                    "Machine Learning Engineer": [
                        "python", "numpy", "pandas",
                        "machine learning", "scikit-learn", "git"
                    ],
                    "Cybersecurity Analyst": [
                        "computer networks", "linux", "python",
                        "operating systems", "sql"
                    ],
                    "Cloud / DevOps Engineer": [
                        "linux", "git", "python",
                        "docker", "cloud", "ci/cd"
                    ]
                }

                # Match career goal using known career categories
                selected_skills = []

                if saved_goal:
                    for career_name, skills in career_skills.items():
                        if career_name.lower() == saved_goal.lower():
                            selected_skills = skills
                            break

                # Basic resume indicators
                education_terms = [
                    "education", "b.tech", "btech", "degree",
                    "university", "college", "cgpa", "qualification"
                ]

                project_terms = [
                    "project", "projects", "developed",
                    "built", "created", "implemented"
                ]

                certification_terms = [
                    "certification", "certifications",
                    "certificate", "certificates"
                ]

                experience_terms = [
                    "experience", "internship", "intern",
                    "work history"
                ]

                def has_any_term(text, terms):
                    return any(term in text for term in terms)

                st.success("Resume text extracted successfully!")

                # Summary metrics
                col1, col2, col3 = st.columns(3)

                col1.metric("PDF Pages", len(reader.pages))
                col2.metric("Skills Identified", len(found_skills))
                col3.metric(
                    "Resume Text",
                    f"{len(resume_text.split())} words"
                )

                st.divider()
                st.subheader("🧩 Skills Found")

                if found_skills:
                    for group, skills in skill_groups.items():
                        group_found = [
                            skill for skill in skills
                            if skill in found_skills
                        ]

                        if group_found:
                            st.write(f"**{group}:**")
                            st.write(", ".join(group_found))
                else:
                    st.warning(
                        "No skills from the built-in checklist were "
                        "identified. Check whether your PDF contains "
                        "readable text and clearly written skill names."
                    )

                st.divider()
                st.subheader("🎯 Career Skill Gap Analysis")

                if selected_skills:
                    missing_skills = [
                        skill for skill in selected_skills
                        if not re.search(
                            r"(?<![a-z0-9+#])"
                            + re.escape(skill)
                            + r"(?![a-z0-9+#])",
                            resume_lower
                        )
                    ]

                    matched_skills = [
                        skill for skill in selected_skills
                        if skill not in missing_skills
                    ]

                    match_percentage = round(
                        len(matched_skills)
                        / len(selected_skills) * 100
                    )

                    st.metric(
                        "Career Checklist Coverage",
                        f"{match_percentage}%"
                    )

                    st.caption(
                        "This percentage measures keyword coverage of "
                        "a starter checklist. It is not a hiring score "
                        "or a measure of actual ability."
                    )

                    st.write("**Keywords found in your resume:**")

                    if matched_skills:
                        st.write(", ".join(matched_skills))
                    else:
                        st.write("No checklist keywords were identified.")

                    st.write("**Skills to consider learning or documenting:**")

                    if missing_skills:
                        for skill in missing_skills:
                            st.write(f"- {skill}")
                    else:
                        st.success(
                            "All checklist keywords were identified. "
                            "Review whether your resume demonstrates "
                            "these skills through real examples."
                        )

                else:
                    st.caption(
                        "Save a supported career goal in Career Goals "
                        "to see a career-specific checklist."
                    )

                st.divider()
                st.subheader("📝 Resume Section Checks")

                checks = {
                    "Education": education_terms,
                    "Projects": project_terms,
                    "Certifications": certification_terms,
                    "Experience or Internships": experience_terms
                }

                for section_name, terms in checks.items():
                    if has_any_term(resume_lower, terms):
                        st.write(f"✅ {section_name} keywords identified")
                    else:
                        st.write(
                            f"⚪ {section_name} keywords not identified"
                        )

                st.caption(
                    "These checks look for keywords only. They cannot "
                    "confirm that a section is complete or accurate."
                )

                st.divider()
                st.subheader("💡 Improvement Suggestions")

                suggestions = []

                if not found_skills:
                    suggestions.append(
                        "Add a clearly labelled Skills section using "
                        "only technologies you genuinely know."
                    )

                if not has_any_term(resume_lower, project_terms):
                    suggestions.append(
                        "Add a Projects section describing what you "
                        "built, which tools you used and what you learned."
                    )

                if not has_any_term(resume_lower, education_terms):
                    suggestions.append(
                        "Make your education details easy to find."
                    )

                if not has_any_term(resume_lower, certification_terms):
                    suggestions.append(
                        "If you have relevant certificates, list their "
                        "names and issuing platforms."
                    )

                if not has_any_term(resume_lower, experience_terms):
                    suggestions.append(
                        "If you have internships or relevant experience, "
                        "describe your actual responsibilities. If not, "
                        "focus on projects and coursework."
                    )

                if selected_skills and missing_skills:
                    suggestions.append(
                        "Compare the missing checklist skills with "
                        "your interests, then learn and practise them "
                        "before adding them to your resume."
                    )

                if not suggestions:
                    suggestions.append(
                        "Review your resume for clear formatting, "
                        "consistent dates, measurable project outcomes "
                        "and accurate skill descriptions."
                    )

                for suggestion in suggestions:
                    st.write(f"- {suggestion}")

                # Optional job description comparison
                if job_description.strip():
                    st.divider()
                    st.subheader("🧾 Job Description Keyword Match")

                    job_lower = job_description.lower()

                    job_keywords = []

                    for skills in skill_groups.values():
                        for skill in skills:
                            pattern = (
                                r"(?<![a-z0-9+#])"
                                + re.escape(skill)
                                + r"(?![a-z0-9+#])"
                            )

                            if (
                                re.search(pattern, job_lower)
                                and skill not in job_keywords
                            ):
                                job_keywords.append(skill)

                    if job_keywords:
                        job_matches = [
                            skill for skill in job_keywords
                            if re.search(
                                r"(?<![a-z0-9+#])"
                                + re.escape(skill)
                                + r"(?![a-z0-9+#])",
                                resume_lower
                            )
                        ]

                        job_missing = [
                            skill for skill in job_keywords
                            if skill not in job_matches
                        ]

                        job_percentage = round(
                            len(job_matches) / len(job_keywords) * 100
                        )

                        st.metric(
                            "Job Keyword Coverage",
                            f"{job_percentage}%"
                        )

                        st.caption(
                            "This is a simple keyword comparison, not "
                            "an employer's ATS score or a prediction "
                            "of whether you will get an interview."
                        )

                        st.write(
                            "**Matching keywords:** "
                            + (
                                ", ".join(job_matches)
                                if job_matches else "None identified"
                            )
                        )

                        st.write(
                            "**Keywords to review:** "
                            + (
                                ", ".join(job_missing)
                                if job_missing else "None from this checklist"
                            )
                        )
                    else:
                        st.info(
                            "No keywords from the built-in skill list "
                            "were found in this job description."
                        )

                with st.expander("📃 View Extracted Resume Text"):
                    st.text(resume_text[:15000])

                    if len(resume_text) > 15000:
                        st.caption(
                            "Preview limited to 15,000 characters."
                        )

            except Exception as error:
                st.error(
                    "Could not read this PDF. Try another text-based "
                    "PDF and check that pypdf is installed."
                )
                st.caption(f"Technical details: {error}")


# =========================================================
# AI MOCK INTERVIEW - SKILLPATH AI
# 24 ROLES | 50 QUESTIONS PER ROLE | 10 RANDOM PER INTERVIEW
# =========================================================

elif page == "AI Mock Interview":
    import random
    import re
    from datetime import date, timedelta

    st.header("🎤 AI Mock Interview")
    st.write(
        "Practise job interviews with role-specific questions, "
        "answer evaluation, sample answers and feedback."
    )

    st.info(
        "Free practice mode. No API key required. "
        "Scores measure keyword coverage, not full AI understanding."
    )

    # -----------------------------------------------------
    # ROLE-WISE TOPICS
    # Each role has 10 topics x 5 question styles = 50.
    # -----------------------------------------------------

    role_topics = {
        "Software Developer": [
            "Object Oriented Programming", "Data Structures",
            "Algorithms", "Time Complexity", "Git Version Control",
            "Debugging", "Exception Handling", "Software Testing",
            "Operating Systems", "Problem Solving"
        ],
        "Web Developer": [
            "HTML", "CSS", "JavaScript", "Responsive Web Design",
            "DOM Manipulation", "REST APIs", "HTTP and HTTPS",
            "Web Accessibility", "Form Validation", "Website Performance"
        ],
        "Data Scientist": [
            "Python for Data Science", "Data Preprocessing",
            "Statistics", "Machine Learning", "Overfitting",
            "Model Evaluation", "Feature Engineering",
            "Data Visualization", "Classification", "Responsible AI"
        ],
        "Data Analyst": [
            "SQL Queries", "Excel Analysis", "Data Cleaning",
            "Mean and Median", "Data Visualization", "Dashboards",
            "KPI Analysis", "Exploratory Data Analysis",
            "Missing Values", "Business Insights"
        ],
        "Java Developer": [
            "Java Classes and Objects", "Inheritance", "Polymorphism",
            "Interfaces", "Abstract Classes", "Collections Framework",
            "Exception Handling", "Multithreading", "JVM and JDK",
            "Java File Handling"
        ],
        "Python Developer": [
            "Python Data Types", "Functions", "Lists and Tuples",
            "Dictionaries and Sets", "Modules and Packages",
            "File Handling", "Exception Handling", "Generators",
            "Object Oriented Python", "Python Testing"
        ],
        "Full Stack Developer": [
            "Frontend Development", "Backend Development", "REST APIs",
            "Database Integration", "Authentication", "State Management",
            "Web Security", "Deployment", "Version Control",
            "Full Stack Architecture"
        ],
        "Frontend Developer": [
            "HTML Semantics", "CSS Flexbox", "CSS Grid",
            "JavaScript DOM", "Responsive Design", "Accessibility",
            "React Components", "Browser Developer Tools",
            "Web Performance", "Form Validation"
        ],
        "Backend Developer": [
            "Server Side Programming", "REST APIs", "Database Queries",
            "Authentication", "Authorization", "Caching",
            "API Security", "Error Handling", "Logging",
            "Backend Performance"
        ],
        "Machine Learning Engineer": [
            "Supervised Learning", "Unsupervised Learning",
            "Feature Engineering", "Training and Testing Data",
            "Overfitting", "Model Deployment", "Model Evaluation",
            "Data Pipelines", "Model Monitoring", "ML Ethics"
        ],
        "AI Engineer": [
            "Artificial Intelligence", "Machine Learning",
            "Neural Networks", "Natural Language Processing",
            "Computer Vision", "Prompt Design", "AI Evaluation",
            "AI Hallucinations", "Responsible AI",
            "AI Application Development"
        ],
        "Cloud Engineer": [
            "Cloud Computing", "Virtual Machines", "Cloud Storage",
            "Cloud Networking", "Access Management", "Scalability",
            "Load Balancing", "Monitoring", "Backup and Recovery",
            "Cloud Security"
        ],
        "DevOps Engineer": [
            "Git", "Continuous Integration", "Continuous Deployment",
            "Docker", "Containers", "Infrastructure as Code",
            "Automated Testing", "Monitoring and Logging",
            "CI CD Pipelines", "Incident Management"
        ],
        "Cybersecurity Analyst": [
            "Network Security", "Phishing Awareness", "Malware Awareness",
            "Authentication", "Encryption", "Access Control",
            "Security Logs", "Vulnerability Assessment",
            "Incident Response", "Security Best Practices"
        ],
        "Database Administrator": [
            "Relational Databases", "SQL Queries",
            "Database Normalization", "Primary and Foreign Keys",
            "Indexes", "Transactions", "Backup and Recovery",
            "Database Security", "Query Optimization",
            "Database Monitoring"
        ],
        "Software Tester / QA Engineer": [
            "Software Testing", "Test Cases", "Test Plans",
            "Regression Testing", "Integration Testing",
            "System Testing", "Bug Reporting", "Automation Testing",
            "Boundary Value Analysis", "Quality Assurance"
        ],
        "Mobile App Developer": [
            "Mobile App Architecture", "User Interface Design",
            "API Integration", "Local Data Storage", "App Permissions",
            "Mobile Testing", "App Performance", "Notifications",
            "Offline Functionality", "Mobile App Security"
        ],
        "C/C++ Developer": [
            "Pointers", "Arrays", "Functions", "Structures",
            "Memory Management", "Object Oriented Programming",
            "References", "STL Containers", "File Handling",
            "Compilation and Debugging"
        ],
        "Data Engineer": [
            "ETL Pipelines", "Data Warehousing", "SQL",
            "Data Modeling", "Batch Processing", "Stream Processing",
            "Data Quality", "Data Integration", "Pipeline Monitoring",
            "Scalable Data Systems"
        ],
        "Business Analyst": [
            "Requirements Gathering", "Stakeholder Communication",
            "Business Process Mapping", "User Stories",
            "Acceptance Criteria", "Gap Analysis",
            "Data Driven Decisions", "Documentation",
            "Prioritization", "Agile Methodology"
        ],
        "UI/UX Designer": [
            "User Research", "Personas", "Wireframes", "Prototyping",
            "Usability Testing", "Information Architecture",
            "Accessibility", "Visual Hierarchy", "Design Systems",
            "User Feedback"
        ],
        "Computer Networks Engineer": [
            "OSI Model", "TCP IP", "IP Addressing", "DNS", "DHCP",
            "Routers and Switches", "TCP and UDP", "Subnetting",
            "Network Troubleshooting", "Network Security"
        ],
        "Embedded Systems Engineer": [
            "Microcontrollers", "Sensors", "Digital and Analog Signals",
            "GPIO Pins", "UART Communication", "I2C Communication",
            "SPI Communication", "Interrupts", "Real Time Systems",
            "Embedded System Testing"
        ],
        "General HR Interview": [
            "Self Introduction", "Strengths and Skills",
            "Areas for Improvement", "Teamwork", "Communication",
            "Problem Solving", "Handling Feedback",
            "Learning New Skills", "Career Goals",
            "Explaining a Project"
        ],
    }

    # -----------------------------------------------------
    # ORIGINAL QUESTIONS - RETAINED
    # These replace the first five generated questions
    # for the original four roles.
    # -----------------------------------------------------

    original_questions = {
        "Software Developer": [
            (
                "What is Object-Oriented Programming (OOP)?",
                ["class", "object", "inheritance", "polymorphism"],
                "OOP organizes programs using classes and objects. Its main principles include encapsulation, inheritance, polymorphism and abstraction."
            ),
            (
                "What is the difference between a list and a tuple in Python?",
                ["mutable", "immutable", "list", "tuple"],
                "A list is mutable, so its elements can change. A tuple is immutable after creation."
            ),
            (
                "What is the purpose of data structures?",
                ["organize", "store", "data", "efficient", "search"],
                "Data structures organize and store data so operations such as searching, insertion and deletion can be performed efficiently."
            ),
            (
                "What is Git and why is it useful?",
                ["version", "control", "changes", "collaboration", "code"],
                "Git is a version control system that tracks code changes and supports collaboration."
            ),
            (
                "Explain one project you have built.",
                ["problem", "features", "technology", "built", "result"],
                "Describe the problem, technologies used, main features, your contribution and the result."
            ),
        ],
        "Web Developer": [
            (
                "What are HTML, CSS and JavaScript used for?",
                ["structure", "style", "interaction", "web", "page"],
                "HTML defines webpage structure, CSS controls appearance and JavaScript adds interaction."
            ),
            (
                "What is responsive web design?",
                ["screen", "device", "media queries", "mobile", "layout"],
                "Responsive design adapts a website to different screen sizes using flexible layouts and media queries."
            ),
            (
                "What is an API?",
                ["application", "interface", "request", "response", "data"],
                "An API allows software applications to communicate by sending requests and receiving responses."
            ),
            (
                "What is the difference between frontend and backend?",
                ["frontend", "user", "backend", "server", "database"],
                "Frontend is the part users interact with. Backend handles server-side logic and data processing."
            ),
            (
                "Explain one website project you have built.",
                ["problem", "html", "css", "javascript", "features"],
                "Describe the website purpose, technologies, features, your contribution and what you learned."
            ),
        ],
        "Data Scientist": [
            (
                "What is the difference between AI, ML and Data Science?",
                ["data", "machine learning", "artificial intelligence", "model"],
                "AI builds systems for intelligent tasks, ML learns patterns from data, and Data Science extracts insights from data."
            ),
            (
                "What is data preprocessing?",
                ["clean", "missing", "duplicate", "transform", "data"],
                "Data preprocessing prepares raw data by handling missing values, duplicates and incorrect formats."
            ),
            (
                "What is overfitting in machine learning?",
                ["training", "unseen", "generalize", "model", "data"],
                "Overfitting occurs when a model fits training data too closely and performs poorly on unseen data."
            ),
            (
                "Why split data into training and testing sets?",
                ["training", "testing", "evaluate", "unseen", "performance"],
                "Training data teaches the model. Testing data evaluates its performance on unseen examples."
            ),
            (
                "What is the purpose of data visualization?",
                ["chart", "graph", "pattern", "insight", "data"],
                "Charts and graphs communicate patterns, trends and insights clearly."
            ),
        ],
        "Data Analyst": [
            (
                "What is SQL used for?",
                ["database", "query", "retrieve", "data", "table"],
                "SQL is used to query and manage relational databases and their tables."
            ),
            (
                "What is the difference between mean and median?",
                ["average", "middle", "value", "outliers"],
                "Mean is the arithmetic average. Median is the middle value in sorted data and is less affected by outliers."
            ),
            (
                "How would you handle missing data?",
                ["identify", "remove", "impute", "median", "missing"],
                "Identify missing values, then remove or impute them using an appropriate method."
            ),
            (
                "What is a dashboard?",
                ["visualization", "metrics", "charts", "data", "decision"],
                "A dashboard presents key metrics and visualizations to support monitoring and decision-making."
            ),
            (
                "Why is data cleaning important?",
                ["accurate", "duplicate", "missing", "errors", "reliable"],
                "Cleaning handles missing values, duplicates and errors to improve data reliability."
            ),
        ],
    }

    # -----------------------------------------------------
    # BUILD EXACTLY 50 QUESTIONS FOR EVERY ROLE
    # -----------------------------------------------------

    question_templates = [
        "Explain {topic} and why it is important in this role.",
        "How would you apply {topic} in a practical project?",
        "What challenges can occur with {topic}, and how would you solve them?",
        "Give a practical example demonstrating your understanding of {topic}.",
        "How would you test or evaluate work involving {topic}?",
    ]

    question_bank = {}

    for role_name, topics in role_topics.items():
        bank = []

        # Create 50 role-topic questions.
        for topic in topics:
            for template in question_templates:
                question = template.format(topic=topic)

                words = list(dict.fromkeys(
                    word.lower()
                    for word in re.findall(r"[a-zA-Z]+", topic)
                    if len(word) > 3
                ))[:5]

                if not words:
                    words = [topic.lower()]

                sample = (
                    f"{topic} is an important area for this role. "
                    f"I would explain its purpose, describe how it works, "
                    f"give a practical example, and explain how I would "
                    f"test the result or solve a related problem."
                )

                bank.append({
                    "q": question,
                    "keywords": words,
                    "sample": sample,
                })

        # Preserve the five original questions in the original four roles.
        if role_name in original_questions:
            for i, (old_q, old_keywords, old_sample) in enumerate(
                original_questions[role_name]
            ):
                bank[i] = {
                    "q": old_q,
                    "keywords": old_keywords,
                    "sample": old_sample,
                }

        question_bank[role_name] = bank

    # Verify all roles have exactly 50 questions.
    if not all(len(qs) == 50 for qs in question_bank.values()):
        st.error("Question bank setup error. Please check the code.")
        st.stop()

    # -----------------------------------------------------
    # ROLE SELECTION
    # -----------------------------------------------------

    role = st.selectbox(
        "Choose your interview role",
        list(question_bank.keys()),
        key="mock_interview_role_v1",
    )

    if st.button("🚀 Start Interview", key="mock_start_v1"):
        st.session_state["mock_active_v1"] = True
        st.session_state["mock_role_v1"] = role
        st.session_state["mock_index_v1"] = 0
        st.session_state["mock_feedback_v1"] = {}
        st.session_state["mock_selected_questions_v1"] = random.sample(
            question_bank[role], 10
        )

    # -----------------------------------------------------
    # INTERVIEW SCREEN
    # -----------------------------------------------------

    if st.session_state.get("mock_active_v1", False):
        active_role = st.session_state.get("mock_role_v1", role)
        questions = st.session_state.get(
            "mock_selected_questions_v1", []
        )
        index = st.session_state.get("mock_index_v1", 0)
        feedback = st.session_state.get("mock_feedback_v1", {})

        st.divider()

        if index >= len(questions):
            
            # Award mock interview XP only once per completed interview.
            completed_interview_id = (
                f"{st.session_state.get('mock_role_v1', active_role)}_"
                f"{id(questions)}"
            )

            if (
                "sf_xp_data_v1" in st.session_state
                and st.session_state.get(
                    "sf_awarded_interview_id_v1"
                ) != completed_interview_id
            ):
                xp_data = st.session_state["sf_xp_data_v1"]

                xp_data["xp"] += 30
                xp_data["completed"].append(
                    "Complete a mock interview"
                )
                xp_data["history"].append({
                    "activity": "Complete a mock interview",
                    "xp": 30,
                    "date": date.today().isoformat(),
                })

                today = date.today().isoformat()
                yesterday = (
                    date.today() - timedelta(days=1)
                ).isoformat()

                last_date = xp_data.get("last_claim_date")

                if last_date == today:
                    pass
                elif last_date == yesterday:
                    xp_data["streak"] += 1
                else:
                    xp_data["streak"] = 1

                xp_data["last_claim_date"] = today
                st.session_state["sf_xp_data_v1"] = xp_data
                # Permanently save the interview reward.
                database.save_skillforge_xp(
                    st.session_state.user_id,
                    xp_data
                )
                st.session_state[
                    "sf_awarded_interview_id_v1"
                ] = completed_interview_id

                st.success(
                    "🏆 Mock Interview completed! You earned +30 XP!"
                )
            evaluated_scores = list(feedback.values())
            percentage = round(
                sum(evaluated_scores) / len(evaluated_scores)
            ) if evaluated_scores else 0

            st.success("🎉 Interview completed!")
            st.metric("Average Keyword Match", f"{percentage}%")
            st.write(f"Role: {active_role}")
            st.write(f"Questions in this interview: {len(questions)}")
            st.write(f"Questions evaluated: {len(evaluated_scores)}")

            if percentage >= 70:
                st.success("Good keyword coverage! Keep practising your explanations.")
            elif percentage >= 40:
                st.info("Good start. Review the sample answers and practise more.")
            else:
                st.warning("Review the concepts and try explaining them in your own words.")

            if st.button("🔄 Try Another Interview", key="mock_retry_v1"):
                st.session_state["mock_index_v1"] = 0
                st.session_state["mock_feedback_v1"] = {}
                st.session_state["mock_selected_questions_v1"] = random.sample(
                    question_bank[active_role], 10
                )
                st.rerun()

        else:
            item = questions[index]

            st.subheader(
                f"{active_role} — Question {index + 1} of {len(questions)}"
            )
            st.progress((index + 1) / len(questions))
            st.write(item["q"])

            answer = st.text_area(
                "Your answer",
                key=f"mock_answer_v3_{active_role}_{index}",
                height=150,
                placeholder="Type your answer in your own words...",
            )

            if st.button(
                "📝 Evaluate Answer",
                key=f"mock_eval_v3_{index}",
            ):
                if not answer.strip():
                    st.warning("Please type an answer before evaluating.")
                else:
                    answer_lower = answer.lower()

                    matched = [
                        word for word in item["keywords"]
                        if re.search(
                            r"\b" + re.escape(word.lower()) + r"\b",
                            answer_lower,
                        )
                    ]

                    score = round(
                        len(matched) / len(item["keywords"]) * 100
                    ) if item["keywords"] else 0

                    st.session_state["mock_feedback_v1"][index] = score

                    st.markdown("### 📊 Feedback")
                    st.metric("Keyword Match", f"{score}%")
                    st.write(
                        f"Relevant keywords found: {len(matched)} "
                        f"out of {len(item['keywords'])}"
                    )

                    missing = [
                        word for word in item["keywords"]
                        if word not in matched
                    ]

                    if missing:
                        st.write(
                            "**Topics you could mention:** "
                            + ", ".join(missing)
                        )

                    if score >= 70:
                        st.success("Good keyword coverage! Explain the concepts clearly.")
                    elif score >= 40:
                        st.info("Fair start. Add relevant concepts and examples.")
                    else:
                        st.warning("Review the sample answer and try explaining it again.")

                    with st.expander("💡 View sample answer"):
                        st.write(item["sample"])

            if index in feedback:
                st.caption(
                    f"Saved keyword match for this question: {feedback[index]}%"
                )

                if st.button(
                    "➡️ Next Question",
                    key=f"mock_next_v3_{index}",
                ):
                    st.session_state["mock_index_v1"] = index + 1
                    st.rerun()

# =========================================================
# SKILLFORGE CODE LAB
# =========================================================


elif page == "SkillForge Code Lab":

    st.header("⚡ SkillForge Code Lab")

    st.markdown(
        """
        ### Your coding workspace

        Write code, run programs, experiment with different languages,
        and learn by building.

        - Multi-language code editor
        - Run button and live output
        - Syntax highlighting
        - Standard input for programs that need input
        - Compiler errors and runtime feedback
        - HTML, CSS and JavaScript web previews where supported
        """
    )

    st.divider()

    st.subheader("🧑‍💻 Start Coding")

    st.caption(
        "Choose a programming language from the editor's language selector. "
        "Write your code, provide input if required, and click Run."
    )

    st.info(
        "Beginner tip: First try a Hello World program. "
        "Then change the message, add variables, and experiment with loops."
    )

    # Embedded online coding editor.
    # The editor runs on the external provider's website.
    editor_url = "https://onecompiler.com/embed/?theme=dark"
    )

    
    st.iframe(
        src=editor_url,
        height=720
    )


    st.divider()

    with st.expander("📌 How to use SkillForge Code Lab"):
        st.markdown(
            """
            1. Select a language in the embedded editor.
            2. Type or edit the sample program.
            3. Enter input in the editor's I/O section if needed.
            4. Click Run to execute the program.
            5. Read the output or compiler error.
            6. Fix the code and run it again.

            **Remember:** Save important code separately in your own
            project files. The editor is an external service, so its
            availability and supported languages may change.
            """
        )

    st.caption(
        "Execution is provided by the embedded external editor. "
        "SkillPath AI does not execute arbitrary code on its own server."
    )

# =========================================================
# SKILLFORGE XP & ACHIEVEMENTS
# =========================================================


elif page == "SkillForge XP & Achievements":
    import streamlit as st
    from datetime import date, timedelta

    st.header("🏆 SkillForge XP & Achievements")
    st.write(
        "Learn consistently, complete activities, earn XP, "
        "unlock badges, and track your growth."
    )

    # Separate session-state keys; no database changes.
    # Load this student's permanent XP data from skillpath.db.
    if "sf_xp_loaded_user_v1" not in st.session_state:
        st.session_state["sf_xp_loaded_user_v1"] = None

    current_user_id = st.session_state.user_id

    if (
        st.session_state["sf_xp_loaded_user_v1"]
        != current_user_id
    ):
        st.session_state["sf_xp_data_v1"] = (
            database.get_skillforge_xp(current_user_id)
        )
        st.session_state["sf_xp_loaded_user_v1"] = (
            current_user_id
        )

    data = st.session_state["sf_xp_data_v1"]

    activities = {
        "Complete a coding practice session": {
            "xp": 20,
            "icon": "💻",
        },
        "Complete a mock interview": {
            "xp": 30,
            "icon": "🎤",
        },
        "Finish a learning module": {
            "xp": 25,
            "icon": "📚",
        },
        "Complete a skill assessment": {
            "xp": 15,
            "icon": "🧠",
        },
        "Improve your resume or portfolio": {
            "xp": 20,
            "icon": "📄",
        },
    }

    def get_level(xp):
        return (xp // 100) + 1

    def get_level_progress(xp):
        return xp % 100

    def get_badges(completed, xp, streak):
        badges = []

        if xp >= 20:
            badges.append(("🌱", "First Steps", "Earn 20 XP"))

        if len(completed) >= 3:
            badges.append(("🎯", "Getting Started", "Complete 3 activities"))

        if len(completed) >= 5:
            badges.append(("🚀", "Consistent Learner", "Complete 5 activities"))

        if xp >= 100:
            badges.append(("⭐", "Century Club", "Earn 100 XP"))

        if xp >= 250:
            badges.append(("💎", "XP Explorer", "Earn 250 XP"))

        if streak >= 3:
            badges.append(("🔥", "3-Day Streak", "Learn on 3 consecutive days"))

        if streak >= 7:
            badges.append(("🏅", "Weekly Warrior", "Learn on 7 consecutive days"))

        return badges

    xp = data["xp"]
    level = get_level(xp)
    progress = get_level_progress(xp)

    st.subheader("📊 Your Dashboard")

    c1, c2, c3 = st.columns(3)
    c1.metric("Total XP", xp)
    c2.metric("Level", level)
    c3.metric("Activities Completed", len(data["completed"]))

    st.progress(progress / 100)
    st.caption(f"{progress}/100 XP towards Level {level + 1}")

    st.divider()

    st.subheader("🎮 Claim Activity Rewards")
    st.caption(
        "Choose an activity you completed today. "
        "Each activity can be claimed once per day."
    )

    today = date.today().isoformat()
    already_claimed_today = {
        item["activity"]
        for item in data["history"]
        if item["date"] == today
    }

    selected_activity = st.selectbox(
        "Select completed activity",
        list(activities.keys()),
        key="sf_selected_activity_v1",
    )

    reward = activities[selected_activity]["xp"]

    st.info(
        f"{activities[selected_activity]['icon']} "
        f"{selected_activity} — Reward: **{reward} XP**"
    )

    if selected_activity in already_claimed_today:
        st.warning("You've already claimed this activity's reward today.")

    if st.button("🎁 Claim XP", key="sf_claim_xp_v1"):
        if selected_activity in already_claimed_today:
            st.warning("This activity has already been claimed today.")
        else:
            data["xp"] += reward
            data["completed"].append(selected_activity)
            data["history"].append({
                "activity": selected_activity,
                "xp": reward,
                "date": today,
            })

            last_date = data["last_claim_date"]

            if last_date == today:
                pass
            elif last_date == (date.today() - timedelta(days=1)).isoformat():
                data["streak"] += 1
            else:
                data["streak"] = 1

            data["last_claim_date"] = today
            st.session_state["sf_xp_data_v1"] = data

            # Permanently save the reward for this student.
            database.save_skillforge_xp(
                st.session_state.user_id,
                data
            )

            st.success(
                f"Congratulations! You earned {reward} XP! 🎉"
            )
            st.rerun()

    st.divider()

    st.subheader("🏅 Achievement Badges")

    badges = get_badges(
        data["completed"],
        data["xp"],
        data["streak"],
    )

    all_badges = [
        ("🌱", "First Steps", "Earn 20 XP"),
        ("🎯", "Getting Started", "Complete 3 activities"),
        ("🚀", "Consistent Learner", "Complete 5 activities"),
        ("⭐", "Century Club", "Earn 100 XP"),
        ("💎", "XP Explorer", "Earn 250 XP"),
        ("🔥", "3-Day Streak", "Learn on 3 consecutive days"),
        ("🏅", "Weekly Warrior", "Learn on 7 consecutive days"),
    ]

    earned_names = {badge[1] for badge in badges}

    cols = st.columns(2)

    for index, (icon, name, description) in enumerate(all_badges):
        with cols[index % 2]:
            if name in earned_names:
                st.success(f"{icon} **{name}**\n\n{description}")
            else:
                st.info(f"🔒 **{name}**\n\n{description}")

    st.divider()

    st.subheader("🔥 Learning Streak")
    st.metric("Current streak", f"{data['streak']} day(s)")
    st.caption(
        "Your streak increases when you claim an activity on consecutive "
        "calendar days. Multiple activities on the same day count as one day."
    )

    st.divider()

    st.subheader("📜 Recent Activity")

    if data["history"]:
        for item in reversed(data["history"][-10:]):
            st.write(
                f"• **{item['activity']}** — "
                f"+{item['xp']} XP · {item['date']}"
            )
    else:
        st.info("No activities yet. Complete your first activity to earn XP!")
        
    if st.button("🔄 Reset XP Demo", key="sf_reset_xp_v1"):
        reset_data = {
            "xp": 0,
            "completed": [],
            "history": [],
            "last_claim_date": None,
            "streak": 0,
        }

        database.save_skillforge_xp(
            st.session_state.user_id,
            reset_data
        )

        st.session_state["sf_xp_data_v1"] = reset_data
        st.rerun()


# =========================================================
# AI CAREER MENTOR
# =========================================================


elif page == "AI Career Mentor":
    st.header("🤖 AI Career Mentor")
    st.write("Your personalized Generative AI career assistant.")

    load_dotenv()

    gemini_api_key = os.getenv("GEMINI_API_KEY")
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

    profile = database.get_profile(st.session_state["user_id"])
    career_goal = database.get_career_goal(st.session_state["user_id"])

    if not career_goal:
        st.warning(
            "Please select your career goal in the Career Goals page "
            "for personalized guidance."
        )

    st.caption(
        "Ask about careers, skills, projects, interviews, or learning roadmaps."
    )

    if "mentor_messages" not in st.session_state:
        st.session_state["mentor_messages"] = []

    for chat_message in st.session_state["mentor_messages"]:
        with st.chat_message(chat_message["role"]):
            st.markdown(chat_message["content"])

    user_question = st.chat_input("Ask your career mentor...")

    if user_question:
        st.session_state["mentor_messages"].append(
            {"role": "user", "content": user_question}
        )

        with st.chat_message("user"):
            st.markdown(user_question)

        answer = None
        provider_errors = []

        profile_context = (
            str(profile) if profile else "Profile not completed"
        )

        system_prompt = (
            "You are SkillPath AI, a friendly career mentor for Indian "
            "engineering students. Give practical, beginner-friendly advice "
            "in simple English. Use headings and bullet points when useful. "
            "Do not invent job openings or claim jobs are verified. "
            f"\nStudent profile: {profile_context}"
            f"\nCareer goal: {career_goal or 'Not selected'}"
        )

        # Recent conversation context
        recent_messages = st.session_state["mentor_messages"][-12:]

        conversation = "\n".join(
            f"{'Student' if msg['role'] == 'user' else 'Mentor'}: "
            f"{msg['content']}"
            for msg in recent_messages
        )

        prompt = (
            f"{system_prompt}\n\n"
            f"Recent conversation:\n{conversation}\n\n"
            f"Answer the student's latest question: {user_question}"
        )

        with st.chat_message("assistant"):
            with st.spinner("Your AI mentor is thinking..."):

                # 1. Try Gemini first
                if gemini_api_key:
                    try:
                        client = genai.Client(api_key=gemini_api_key)

                        response = client.models.generate_content(
                            model="gemini-3.1-flash-lite",
                            contents=prompt,
                            config={
                                "temperature": 0.4,
                                "max_output_tokens": 600
                            }
                        )

                        if response.text and response.text.strip():
                            answer = response.text.strip()
                        else:
                            provider_errors.append(
                                "Gemini returned an empty response."
                            )

                    except Exception as e:
                        provider_errors.append(
                            f"Gemini error: {str(e)[:300]}"
                        )
                else:
                    provider_errors.append(
                        "GEMINI_API_KEY is missing from .env."
                    )

                # 2. If Gemini fails, try OpenRouter backup
                if not answer and openrouter_api_key:
                    headers = {
                        "Authorization": f"Bearer {openrouter_api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://skillpath-ai.onrender.com",
                        "X-Title": "SkillPath AI"
                    }

                    messages = [
                        {
                            "role": "system",
                            "content": system_prompt
                        }
                    ]
                    messages.extend(recent_messages)

                    models = [
                        "google/gemma-4-26b-a4b-it:free",
                        "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"
                    ]

                    for model_name in models:
                        try:
                            response = requests.post(
                                "https://openrouter.ai/api/v1/chat/completions",
                                headers=headers,
                                json={
                                    "model": model_name,
                                    "messages": messages,
                                    "temperature": 0.4,
                                    "max_tokens": 600
                                },
                                timeout=40
                            )

                            if response.status_code != 200:
                                provider_errors.append(
                                    f"OpenRouter {model_name}: HTTP "
                                    f"{response.status_code}"
                                )
                                continue

                            data = response.json()
                            choices = data.get("choices", [])

                            if choices:
                                content = choices[0].get(
                                    "message", {}
                                ).get("content")

                                if isinstance(content, str) and content.strip():
                                    answer = content.strip()
                                    break

                        except Exception as e:
                            provider_errors.append(
                                f"OpenRouter {model_name}: {str(e)[:200]}"
                            )

                # 3. If both APIs fail, use existing offline guidance
                if answer:
                    st.markdown(answer)
                else:
                    answer = get_offline_career_guidance(
                        user_question, career_goal
                    )

                    st.info(
                        "AI providers are currently unavailable. "
                        "Showing built-in career guidance instead."
                    )
                    st.markdown(answer)

                if provider_errors:
                    with st.expander("AI connection diagnostics"):
                        for error in provider_errors:
                            st.write(error)

        st.session_state["mentor_messages"].append(
            {"role": "assistant", "content": answer}
        )



# =========================================================
# MY PROGRESS
# =========================================================

elif page == "My Progress":
    st.header("📈 My Progress")

    history = database.get_assessment_history(
        st.session_state.user_id
    )

    if history:
        st.subheader("Assessment Performance")

        for attempt in history:
            percentage = round(
                attempt["score"] / attempt["total_questions"] * 100
            )

            st.write(
                f"**{attempt['career_goal']}** — "
                f"{attempt['score']}/{attempt['total_questions']} "
                f"({percentage}%)"
            )

            st.progress(percentage / 100)

        average_score = sum(
            attempt["score"] / attempt["total_questions"] * 100
            for attempt in history
        ) / len(history)

        st.metric(
            "Average Assessment Score",
            f"{round(average_score)}%"
        )
    else:
        st.info(
            "Complete your first Skill Assessment to start tracking "
            "your progress."
        )
