import openai
import speech_recognition as sr
from googletrans import Translator
from fpdf import FPDF
import os

# Set your OpenAI API key
openai.api_key = 'your-api-key'

# Initialize translator
translator = Translator()

# Predefined list of symptoms
SYMPTOMS = ['fever', 'cough', 'headache', 'cold', 'fatigue', 'nausea', 'vomiting', 'dizziness', 'diarrhea']

# Function to extract symptoms from the user query
def extractSymptoms(text):
    return [symptom for symptom in SYMPTOMS if symptom in text.lower()]

# Function to record and transcribe voice input
def getVoiceInput():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️ Speak now...")
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio)
            print("📝 You said:", text)
            return text
        except sr.UnknownValueError:
            print("❌ Could not understand audio")
            return None
        except sr.RequestError as e:
            print("🔌 Could not request results; {0}".format(e))
            return None

# Function to detect language
def detectLanguage(text):
    return translator.detect(text).lang

# Function to translate to English
def translateToEnglish(text):
    return translator.translate(text, dest='en').text

# Function to translate from English
def translateFromEnglish(text, dest_lang):
    return translator.translate(text, dest=dest_lang).text

# Function to generate OpenAI response
def generateResponse(prompt):
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            {"role": "system", "content": "You are a helpful and knowledgeable health assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content'].strip()

# Function to generate PDF report
def generatePDF(userText, botResponse, symptoms, lang):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="HealthBot Consultation Report", ln=True, align='C')
    pdf.ln(10)
    
    pdf.multi_cell(0, 10, f"🗣️ User Query ({lang}):\n{userText}\n", align='L')
    pdf.multi_cell(0, 10, f"💬 Chatbot Response ({lang}):\n{botResponse}\n", align='L')
    if symptoms:
        pdf.multi_cell(0, 10, f"⚠️ Detected Symptoms:\n{', '.join(symptoms)}\n", align='L')

    report_path = "health_report.pdf"
    pdf.output(report_path)
    print(f"📄 PDF report saved as {report_path}")

# Main chatbot function
def chatbot():
    print("Welcome to the Multilingual Voice HealthBot! 🩺")
    print("Say your health concern or type it below.\n")

    # Choose input mode
    choice = input("Do you want to use voice input? (y/n): ").strip().lower()
    if choice == 'y':
        userText = getVoiceInput()
    else:
        userText = input("📝 Enter your health concern: ")

    if not userText:
        print("❌ No input provided.")
        return

    # Detect language
    lang = detectLanguage(userText)
    print(f"🌐 Detected language: {lang}")

    # Translate to English
    userTextEnglish = translateToEnglish(userText)

    # Extract symptoms
    symptoms = extractSymptoms(userTextEnglish)

    # Get response
    botResponseEnglish = generateResponse(userTextEnglish)

    # Translate response back
    botResponseTranslated = translateFromEnglish(botResponseEnglish, lang)

    # Show response
    print(f"\n🤖 Chatbot response ({lang}):\n{botResponseTranslated}")

    # Generate PDF report
    generatePDF(userText, botResponseTranslated, symptoms, lang)

# Run the bot
if __name__ == "__main__":
    chatbot()
