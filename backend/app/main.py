from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import asyncio
import os
import boto3
from dotenv import load_dotenv
import anthropic

# Load environment variables
load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

app = FastAPI(title="GlassSlipper.ai")

# Allow frontend to call backend
origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AWS Rekognition setup
rekognition_client = boto3.client('rekognition', region_name='us-east-2')

def get_makeup_recommendations(traits):
    prompt = f"""
    Given the following facial traits:
    {traits}

    Suggest makeup products, clothing, and jewelry/accessories suitable for these traits.

    You MUST format your response exactly as follows:
    - Use ### headings to separate sections: "Drugstore Makeup", "High-End Makeup", "Clothing Suggestions", "Jewelry & Accessories", and "Application Tips"
    - Under each section, list every recommendation as a bullet point using "-"
    - For makeup sections, each bullet should follow the format: **Product Type** — Brand Shade Name
    - Both "Drugstore Makeup" and "High-End Makeup" must recommend the same product categories (e.g., if you suggest a foundation, blush, lipstick, and mascara in Drugstore, suggest a foundation, blush, lipstick, and mascara in High-End too)
    - Include 4-5 product recommendations per makeup section
    - For "Clothing Suggestions", recommend 3-4 outfit pieces or styles that complement the person's features, using the format: **Item** — Description
    - For "Jewelry & Accessories", recommend 3-4 pieces (e.g., earrings, necklaces, hair accessories) using the format: **Item** — Description
    - Under "Application Tips", list 3-4 brief tips as bullet points using "-"
    - Do NOT use numbered lists, tables, or any other formatting
    """
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


# Upload image & detect celebrities
@app.post("/upload/demo_user")
async def upload_image(file: UploadFile = File(...)):
    # Save uploaded file temporarily
    upload_folder = "uploads"
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Call Amazon Rekognition
    with open(file_path, "rb") as image_file:
        image_bytes = image_file.read()
        try:
            celeb_response = rekognition_client.recognize_celebrities(Image={'Bytes': image_bytes})
            traits_response = rekognition_client.detect_faces(Image={'Bytes': image_bytes}, Attributes=['ALL'])
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # Build a lookup of celebrity names by bounding box position
    celeb_names = []
    for celeb in celeb_response.get("CelebrityFaces", []):
        box = celeb['Face']['BoundingBox']
        celeb_names.append({
            "name": celeb['Name'],
            "left": box['Left'],
            "top": box['Top'],
        })

    def match_celebrity(face_box):
        """Match a detected face to a celebrity by closest bounding box position."""
        best = None
        best_dist = float('inf')
        for c in celeb_names:
            dist = abs(c['left'] - face_box['Left']) + abs(c['top'] - face_box['Top'])
            if dist < best_dist:
                best_dist = dist
                best = c['name']
        return best if best_dist < 0.1 else None

    # Process faces
    face_data = []
    for face in traits_response.get("FaceDetails", []):
        celebrity_name = match_celebrity(face['BoundingBox'])
        traits_info = {
            "Gender": face['Gender']['Value'],
            "AgeRange": face['AgeRange'],
            "Emotions": [e['Type'] for e in face['Emotions'] if e['Confidence'] > 50],
            "Smile": face['Smile']['Value'],
            "Eyeglasses": face['Eyeglasses']['Value'],
            "Sunglasses": face['Sunglasses']['Value'],
            "Beard": face['Beard']['Value'],
            "Mustache": face['Mustache']['Value'],
            "EyesOpen": face['EyesOpen']['Value'],
            "MouthOpen": face['MouthOpen']['Value'],
            "Pose": face['Pose']
        }
        face_result = {
            "name": celebrity_name,
            "gender": traits_info["Gender"],
            "ageRange": {"Low": traits_info["AgeRange"]["Low"], "High": traits_info["AgeRange"]["High"]},
            "emotions": traits_info["Emotions"],
            "smile": traits_info["Smile"],
            "eyeglasses": traits_info["Eyeglasses"],
            "sunglasses": traits_info["Sunglasses"],
            "beard": traits_info["Beard"],
            "mustache": traits_info["Mustache"],
            "eyesOpen": traits_info["EyesOpen"],
            "mouthOpen": traits_info["MouthOpen"],
            "pose": {
                "Pitch": traits_info["Pose"]["Pitch"],
                "Roll": traits_info["Pose"]["Roll"],
                "Yaw": traits_info["Pose"]["Yaw"],
            },
            "makeupRecommendations": "",
        }
        face_data.append((face_result, traits_info))

    # Generate makeup recommendations concurrently for all faces
    async def fetch_recommendations(face_result, traits_info):
        try:
            rec = await asyncio.to_thread(get_makeup_recommendations, traits_info)
            face_result["makeupRecommendations"] = rec
        except Exception as e:
            print(f"Claude API error: {e}")
            face_result["makeupRecommendations"] = "Makeup recommendations are currently unavailable."

    await asyncio.gather(*[fetch_recommendations(fr, ti) for fr, ti in face_data])

    return {"filename": file.filename, "faces": [fr for fr, _ in face_data]}




@app.get("/test-claude", response_class=HTMLResponse)
async def test_claude():
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": "Give me 3 quick makeup tips."}],
        )
        html_content = f"<h1>Claude Recommendations</h1><p>{response.content[0].text}</p>"
        return HTMLResponse(content=html_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
