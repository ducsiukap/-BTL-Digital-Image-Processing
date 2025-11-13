from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse as res, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import imageio.v3 as iio
import numpy as np
import io 
import os
import uuid
from utils.ImageProcessing import ImageProcessing

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def home(): return {"message": "helloworld"}

@app.get("/api/health")
async def api_check(): return {"message": "api is running..."}

@app.post("/api/image/upload")
async def uploadImage(file: UploadFile = File(...)):
    fileContent = await file.read()

    try: 
        img = iio.imread(io.BytesIO(fileContent))
        # img.shape = (height, width, channel) // channel=3 => (R,G,B), channel=4 => (R,G,B,A)
        # image.shape = (height, width) // gray image

        # lay anh xam
        if len(img.shape) == 3 and img.shape[2] == 3: # rgb
            # (h, w, 3) => (h, w) 
            # img.shape[2] = (R, G, B) => grayValue # mean(R, G, B)
            imgGray = np.mean(img, axis=2).astype(np.uint8)
            imgExt = '.png'
        else: 
            imgGray = img
            imgExt = os.path.splitext(file.filename)[1]

        # luu anh 
        savePath = os.path.join("uploads", f"{uuid.uuid4().hex}{imgExt}")
        iio.imwrite(savePath, imgGray)
        # print(img)
        # print(imgGray)

        # response
        return res(content={"imagePath": savePath})
    except Exception as e: 
        return res(content={"message": str(e)}, status_code=400)
    
@app.get("/api/image-process/threshold-otsu")
async def otsuThresholding(imagePath: str):
    response = ImageProcessing.threshold_otsu(imagePath)
    if not response["success"]:
        return res(content={"message": response["message"]}, status_code=400)
    else:
        return StreamingResponse(response["bytes"], media_type="image/png")