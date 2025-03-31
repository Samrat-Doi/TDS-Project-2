import os
from fastapi import FastAPI, Form, File, UploadFile , HTTPException
import google.generativeai as genai
from dotenv import load_dotenv
import zipfile
import io

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Configure Google Gemini API
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Set it in the .env file.")

genai.configure(api_key=GOOGLE_API_KEY)

@app.post("/api/")
async def process_question(
    question: str = Form(...), file: UploadFile = File(None)
):
    extracted_text = ""
    
    if file:
        if not file.filename.endswith(".zip"):
            raise HTTPException(status_code=400, detail="Only .zip files are supported")
        
        # Read and extract zip file
        contents = await file.read()
        with zipfile.ZipFile(io.BytesIO(contents), "r") as zip_ref:
            for filename in zip_ref.namelist():
                with zip_ref.open(filename) as f:
                    extracted_text += f.read().decode("utf-8") + "\n"
        
        # Construct the prompt with extracted text
        prompt = f"Answer this question in one word or number only: {question}\n{extracted_text}"
    else:
        # Construct the prompt without extracted text
        prompt = f"Answer this question in one word or number only: {question}"
    

    print(prompt)
    
    # Get response from Gemini
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    
    # Extract answer (clean response)
    answer = response.text.strip() if response.text else "Could not generate answer."
    
    return {"answer": answer}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

