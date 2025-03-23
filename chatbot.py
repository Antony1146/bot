import streamlit as st
import pandas as pd
import google.generativeai as genai
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide")

# Initialize session state for users database (Persistent)
if "users_db" not in st.session_state:
    st.session_state.users_db = {}  # Stores registered users

def signup_user(username, password):
    """Register a new user if they don't exist."""
    if username in st.session_state.users_db:
        return False  # User already exists
    st.session_state.users_db[username] = password
    return True  # Signup successful

def login_user(username, password):
    """Check if user exists and password matches."""
    return st.session_state.users_db.get(username) == password

# Initialize session state for authentication
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None

# **Authentication Section**
def login():
    st.subheader("🔐 Login")
    username = st.text_input("Username:")
    password = st.text_input("Password:", type="password")
    if st.button("Login"):
        if login_user(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Welcome, {username}! 🎉")
            st.rerun()  # Refresh the app to show the main content
        else:
            st.error("Invalid username or password! ❌")

def signup():
    st.subheader("📝 Sign Up")
    new_user = st.text_input("Create a Username:")
    new_pass = st.text_input("Create a Password:", type="password")
    if st.button("Sign Up"):
        if signup_user(new_user, new_pass):
            st.success("Account created successfully! ✅ Now log in.")
        else:
            st.error("Username already taken! ❌")

# If not logged in, show login/signup options
if not st.session_state.logged_in:
    page = st.radio("Choose an option:", ["Login", "Sign Up"])
    if page == "Login":
        login()
    else:
        signup()
    st.stop()  # Stop execution until user logs in

# **Main App Content (Only for Logged-in Users)**
st.success(f"✅ Logged in as {st.session_state.username}")

# Configure Google AI
genai.configure(api_key="AIzaSyD_dJMha8VcX_EvPJ2YsDrpaBs-H8hH8Vs")
model = genai.GenerativeModel("gemini-1.5-flash-latest")

# Inject Custom CSS for Styling
st.markdown("""
    <style>
    body {
        background-color: #f0f2f6;
        color: #333333;
        font-family: 'Arial', sans-serif;
    }
    .stApp {
        background-color: #faf5eb;
        border-radius: 10px;
        padding: 20px;
    }
    .stFileUploader{
        background-color: orange;
        border: 2px solid orange;
        border-radius: 10px;
        padding: 50px;
    }
    .header-container {
        background-color: black;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20px;
        width: 100%;
    }
    .title {
        background-color: orange;
        border-radius: 10px;
        font-size: 28px;
        font-weight: bold;
        color: white;
        margin: 20px;
        padding-left: 20px;
        text-align: center;
    }
    .subheader {
        color: orange;
        margin-top: 50px;
    }
    .stButton>button{
        background-color: orange;
        color: white;
        
    }
    </style>
    <div class="header-container">
        <div class="title"><h2>AntBot Data Analysis</h2></div>
    </div>
    <div class="subheader"><h3>Upload a dataset and ask questions!</h3></div>
""", unsafe_allow_html=True)

# File Upload
uploaded_file = st.file_uploader("📂 Upload your dataset (CSV)", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("### 🔍 Dataset Preview:")
    st.write(df.head())

    # Column selection
    column = st.selectbox("Select a column to visualize", df.columns)

    # Graph Type Selection
    graph_type = st.selectbox("Choose a graph type", ["Histogram", "Bar Chart", "Pie Chart", "Scatter Plot"])

    # Plot Graph
    st.write(f"### 📊 {graph_type} for {column}")
    fig, ax = plt.subplots()

    if graph_type == "Histogram":
        sns.histplot(df[column], bins=20, kde=True, ax=ax, color="#f5b342")
    elif graph_type == "Bar Chart":
        df[column].value_counts().plot(kind="bar", ax=ax, color="#f5b342")
    elif graph_type == "Pie Chart":
        df[column].value_counts().plot(kind="pie", autopct='%1.1f%%', ax=ax, colors=sns.color_palette("pastel"))
    elif graph_type == "Scatter Plot":
        other_column = st.selectbox("Select another column for scatter plot", df.columns)
        sns.scatterplot(x=df[column], y=df[other_column], ax=ax, color="#f5b342")

    st.pyplot(fig)

    # User Query
    question = st.text_input("❓ Ask a question about the dataset:")
    if st.button("💡 Get Answer") and question:
        prompt = f"Analyze this dataset and answer: {question}\n\n{df.to_string()}"
        response = model.generate_content(prompt)
        st.write("### 🤖 AI Answer:", response.text)

# Logout Button
if st.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.session_state.username = None
    st.rerun()