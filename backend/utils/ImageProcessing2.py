import imageio.v3 as iio
import io 
import numpy as np

class ImageProcessing2: 
    @staticmethod
    def thresholdOtsu(imagePath):
        try :
            img = iio.imread(imagePath)

            # max, min pixel
            maxGray = img.max()
            minGray = img.min()
            # print(maxGray, minGray)

            # i
            grays = np.arange(0, 256)

            # h(i)
            h, _ = np.histogram(img.flatten(), bins=256, range=[0, 256])
            # p(i)
            p = h / h.sum()

            # p_i(k) 
            p_i = np.cumsum(p)

            # m(i)
            m = []
            prev = 0
            for g in grays:
                # m_g(k) = total(i*p(i)) for i in range(0, g]
                m.append(g*p[g] + prev)
                prev = m[-1]
            m = np.array(m)

            # mG 
            mG = m[-1]
            
            sigma2B = []
            for g in grays:
                # (mG.Pg(k) - m(k))^2
                # /
                # (Pg(k)*(1 - Pg(k)))
                if g < minGray or g >= maxGray: 
                    sigma2B.append(0)
                else:
                    otsuValue = (mG*p_i[g] - m[g])**2 / (p_i[g]*(1 - p_i[g]))
                    sigma2B.append(otsuValue)

            # print(sigma2B)
            otsuThreshold = np.argmax(sigma2B)
            # print(otsuThreshold, sigma2B[otsuThreshold])

            # output
            outImg = (img > otsuThreshold).astype(np.uint8)*255

            img_bytes = io.BytesIO()
            # iio.imwrite(img_bytes, img, extension=".png")
            iio.imwrite(img_bytes, outImg, extension=".png")
            img_bytes.seek(0)

            return {"success": True, "bytes": img_bytes}
        except Exception as e:
            return {"success": False, "message": str(e)}
        
    @staticmethod
    def KmeanPlusPlus(imagePath, nCluster):
        try :
            img = iio.imread(imagePath)
            imgShape = img.shape
            if (img.shape[2] != 3):
                return {"success": False, "message": "image is not is RGB image."}
            img = img.reshape(-1, 3)
            # print(img)

            rgb, indices,h = np.unique(img, axis=0, return_counts=True, return_inverse=True)
            # print(rgb.shape, indices.shape)
            colors = len(rgb)
            maximunCluster = min(100, colors)
            K = min(nCluster, maximunCluster)

            # init cluster
            clusters = np.zeros((K, 3), dtype=np.float64)
            D2min = np.full(colors, np.inf)
            allIndices = np.arange(colors)
            clusterIndices = []
            
            # C0
            idx = np.random.randint(colors)
            clusters[0] = rgb[idx]
            clusterIndices.append(idx)

            # print(clusters)

            # C1-CN
            for i in range(1, K):
                clusterNew = clusters[i-1]
                D2minNew = np.sum((rgb - clusterNew)**2, axis=1)
                np.minimum(D2min, D2minNew, out=D2min)
                W = D2min*h
                W[clusterIndices] = 0
                sumW = np.sum(W)
                
                if (sumW == 0):
                    selectableIndices = np.setdiff1d(allIndices, clusterIndices)
                    if not selectableIndices.any(): break
                    idx = np.random.choice(selectableIndices)
                else:
                    P = W / sumW
                    idx = np.random.choice(allIndices, p=P)
                
                clusters[i] = rgb[idx]
                clusterIndices.append(idx)
            
            # print(grayCluster)
            # print('hi')

            clusterLabel = np.zeros(colors, dtype=np.int32)
            maximumLoopCount = 100
            euclide = 0.01
            for loop in range(maximumLoopCount):
                distance = rgb[:, np.newaxis, :] - clusters[np.newaxis, :, :]
                D2 = np.sum(distance**2, axis=2)

                newLabels = np.argmin(D2, axis=1)
                newClusters = np.zeros_like(clusters)

                for k in range(K):
                    mask = (newLabels == k)
                    if not np.any(mask):
                        newClusters[k] = clusters[k]
                        continue
                    
                    clusterPoint = rgb[mask]
                    clusterH = h[mask]
                    newClusters[k] = np.sum(clusterPoint*clusterH[:, np.newaxis], axis=0)/np.sum(clusterH)
            
                clusterDiff = np.sum((newClusters - clusters)**2)
                clusters = newClusters
                clusterLabel = newLabels

                if clusterDiff <= euclide:
                    print(f"loop count: {loop}")
                    break

            labels = clusterLabel[indices]
            outImgFlat = clusters[labels].astype(np.uint8)
            outImg = outImgFlat.reshape(imgShape)

            img_bytes = io.BytesIO()
            # iio.imwrite(img_bytes, img, extension=".png")
            iio.imwrite(img_bytes, outImg, extension=".jpg")
            img_bytes.seek(0)

            return {"success": True, "bytes": img_bytes, 'clusters': maximunCluster}
        except Exception as e:
            return {"success": False, "message": str(e)}
