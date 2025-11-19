from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse as res, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import imageio.v3 as iio
import numpy as np
import io 
import os
import uuid
from utils.ImageProcessing import ImageProcessing
from utils.ImageProcessing2 import ImageProcessing2

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Max-Cluster"], 
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
        print(img.shape)
        # lay anh xam
        if len(img.shape) == 3: # rgb / rgba
            if img.shape[2] == 4: 
                img = img[:, :, :3]
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
    
@app.get("/api/image-process/threshold/otsu")
async def otsuThresholding(imagePath: str):
    response = ImageProcessing.thresholdOtsu(imagePath)
    if not response["success"]:
        return res(content={"message": response["message"]}, status_code=400)
    else:
        return StreamingResponse(response["bytes"], media_type="image/png")
    
@app.get("/api/image-process/segmentation/kmeanpp")
async def kmeanStardard(imagePath: str, nCluster:int = 2):
    response = ImageProcessing.KmeanPlusPlus(imagePath, nCluster)
    if not response["success"]:
        return res(content={"message": response["message"]}, status_code=400)
    else:
        headers = {
            'X-Max-Cluster': str(response['clusters'])
        }
        # print(headers)
        return StreamingResponse(response["bytes"], media_type="image/png", headers=headers)
    

# API v2
@app.post("/api/v2/image/upload")
async def uploadImage(file: UploadFile = File(...)):
    fileContent = await file.read()

    try: 
        img = iio.imread(io.BytesIO(fileContent))
        # img.shape = (height, width, channel) // channel=3 => (R,G,B), channel=4 => (R,G,B,A)
        # image.shape = (height, width) // gray image

        # lay anh xam
        if len(img.shape) == 3: # rgb / rgba
            if img.shape[2] == 4: 
                img = img[:, :, :3]
            # (h, w, 3) => (h, w) 
            # img.shape[2] = (R, G, B) => grayValue # mean(R, G, B)
            imgGray = np.mean(img, axis=2).astype(np.uint8)
            imgExt = '.png'
        else: 
            imgGray = img
            imgExt = os.path.splitext(file.filename)[1]

        # luu anh xam
        savePath = os.path.join("uploads", f"{uuid.uuid4().hex}{imgExt}")
        iio.imwrite(savePath, imgGray)

        # luu anh mau
        colorImgPath = os.path.join("uploads", f"{uuid.uuid4().hex}{os.path.splitext(file.filename)[1]}")
        iio.imwrite(colorImgPath, img)
        # print(img)
        # print(imgGray)

        # response
        return res(content={"grayImgPath": savePath, "rgbImgPath": colorImgPath})
    except Exception as e: 
        return res(content={"message": str(e)}, status_code=400)
      
@app.get("/api/v2/image-process/threshold/otsu")
async def otsuThresholding(imagePath: str):
    response = ImageProcessing.thresholdOtsu(imagePath)
    if not response["success"]:
        return res(content={"message": response["message"]}, status_code=400)
    else:
        return StreamingResponse(response["bytes"], media_type="image/png")
    
@app.get("/api/v2/image-process/segmentation/kmeanpp")
async def kmeanStardard(imagePath: str, nCluster:int = 2):
    response = ImageProcessing2.KmeanPlusPlus(imagePath, nCluster)
    if not response["success"]:
        return res(content={"message": response["message"]}, status_code=400)
    else:
        headers = {
            'X-Max-Cluster': str(response['clusters'])
        }
        # print(headers)
        return StreamingResponse(response["bytes"], media_type="image/png", headers=headers)