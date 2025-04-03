import os
import openai
import pandas as pd
import speech_recognition as sr
import requests
import configparser
from openai import OpenAI
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from main import main_with_sentiment

# Load API key securely
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Get project root
DATA_FOLDER = os.path.join(BASE_DIR, "data")
EXCEL_FILE = os.path.join(DATA_FOLDER, "CustomerData.xlsx") 
config = configparser.ConfigParser()
config.read(os.path.join(BASE_DIR, "utils" ,"config.ini"))
openai_key = config.get("OPENAI_KEY", "key")

# Initialize OpenAI client
client = OpenAI(api_key=openai_key)

# Try loading dataset at startup
try:
    df = pd.read_excel(EXCEL_FILE)  
except Exception as e:
    print("Error loading dataset:", str(e))
    df = None  # Set to None if loading fails

def get_usernames():
    # Load all sheets from the Excel file
    xls = pd.ExcelFile(EXCEL_FILE)
    usernames = []

    # Iterate through all sheets
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name)  # Read each sheet
        if "Customer_Id" in df.columns:  # Ensure the column exists
            usernames.extend(df["Customer_Id"].dropna().astype(str).tolist())

    return usernames

def login_view(request):
    """Login with a Customer ID (password ignored)."""
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        if username in get_usernames():
            request.session["user"] = username  # Store session
            notification_data = main_with_sentiment(username)
            if "Best regards" in notification_data:
                notification_data = notification_data.split("Best regards")[0].strip() + "\nBest regards,"
            request.session["notification"] = notification_data  # Store in session

            return redirect("index")
        else:
            return render(request, "login.html", {"error": "Invalid Customer ID"})
    return render(request, "login.html")

def index_view(request):
    """Ensure the user is logged in before accessing the index page."""
    if "user" not in request.session:
        return redirect("login")
    customer_id = request.session["user"]
    notification = request.session.get("notification", "No new notifications")

    return render(request, "index.html", {
        "customer_id": customer_id,
        "notification": notification
    })



# Function to find supported files
def get_supported_files(folder_path):
    """Find all supported files in a directory."""
    supported_files = []
    
    for file in os.listdir(folder_path):
        full_path = os.path.join(folder_path, file)

        if file.endswith(".xlsx"):
           converted_files = convert_excel_to_text(full_path)
           if converted_files:  # Ensure it's not None
               supported_files.extend(converted_files)  # Append multiple files
            #print("xlsx file bypassed convertion")
        elif file.endswith((".txt", ".csv", ".json")):
            supported_files.append(full_path)

    return supported_files

# Function to convert Excel to text
def convert_excel_to_text(excel_path):
    """Convert all sheets in an Excel file to text format for vector storage."""
    try:
        sheets = pd.read_excel(excel_path, sheet_name=None, dtype=str)  
        output_dir = os.path.dirname(excel_path)
        base_name = os.path.splitext(os.path.basename(excel_path))[0]
        text_files = []

        for sheet_name, df in sheets.items():
            text_data = df.to_csv(sep="\t", index=False)  
            text_file = os.path.join(output_dir, f"{base_name}_{sheet_name}.txt")

            with open(text_file, "w", encoding="utf-8") as f:
                f.write(text_data)

            text_files.append(text_file)

        return text_files  # Return list of text files
    except Exception as e:
        print(f"Error converting {excel_path}: {e}")
        return None

# Get all files from the folder
files_to_upload = get_supported_files(DATA_FOLDER)

# Create a vector store
vector_store = client.vector_stores.create(name="Support FAQ")

# Upload each file
for file_path in files_to_upload:
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            print(f"Uploading file: {file_path}")
            client.vector_stores.files.upload_and_poll(vector_store_id=vector_store.id, file=f)
    else:
        print(f"Error: File '{file_path}' does not exist.")

print("All files uploaded successfully!")

# Extract relevant information
def extract_relevant_info(results):
    all_texts = [content.text for response in results.data for content in response.content]
    return all_texts



# Retrieve relevant context
def retrieve_relevant_context(query):
    results = client.vector_stores.search(
        vector_store_id=vector_store.id,
        query=query,
    )

   
    if results.data:
        return extract_relevant_info(results)
    else:
        return "No relevant data found."

# Generate AI response
def generate_ai_response(prompt):
    try:
        retrieved_context = retrieve_relevant_context(prompt)

        print("Retrieved Context")

        final_prompt = f"Context:\n{retrieved_context}\n\nUser Query:\n{prompt}"

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": final_prompt}]
        )

        return completion.choices[0].message.content.strip()
    except Exception as e:
        print("Error:", str(e))
        return "I'm having trouble generating a response right now. Please try again later."

# Django Views
def index(request):
    return render(request, 'index.html')

@csrf_exempt
def text_search(request):
    if "user" not in request.session:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    customer_id = request.session["user"]

    if request.method == "POST":
        query = request.POST.get('query', '').strip()
        if not query:
            return JsonResponse({"response": "Please enter a valid query."})

        response = generate_ai_response(f"customer {customer_id} is asking you a query. Based on the data available, provide a response as financial advisor by understanding their sentiment. Do not ask more questions. Provide user with data points explaining rationale behind your response. Respond based on available information, otherwise tell them that you don't have the answer and they can call customer care. Customer Query is: {query}")
        return JsonResponse({"response": response})

    return JsonResponse({"error": "Invalid request method"}, status=400)

@csrf_exempt
def voice_search(request):
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        try:
            audio = recognizer.listen(source)
            text = recognizer.recognize_google(audio).strip()

            if not text:
                return JsonResponse({"response": "No speech detected, please try again."})

            response = generate_ai_response(text)
            return JsonResponse({"response": response})

        except sr.UnknownValueError:
            return JsonResponse({"response": "Sorry, I couldn't understand the audio."})
        except sr.RequestError:
            return JsonResponse({"response": "Could not request results, please try again."})