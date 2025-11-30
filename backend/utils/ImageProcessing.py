import imageio.v3 as iio
import io 
import numpy as np

class ImageProcessing: 
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
            g, h = np.unique(img, return_counts=True)
            g = g.tolist()
            h = h.tolist()
            maximumCluster = len(g)

            # C0
            grayCluster = {}
            cluster = np.random.choice(g)
            grayCluster[cluster] = 0
            index = g.index(cluster)
            g.pop(index)
            h.pop(index)

            # C1-CN
            for k in range(1, nCluster):
                W = [] #W(x)
                for i in range(len(g)):
                    D2min = 256**2
                    for c in grayCluster.values():
                        D2min = min(D2min, (int(g[i]) - int(c))**2)
                    W.append(D2min * h[i])
                
                # P(x)
                sumW = sum(W)
                if sumW == 0:
                    index = np.random.randint(len(g))
                    grayCluster[g[index]] = k
                    g.pop(index)
                    h.pop(index)
                else:
                    P = np.cumsum(np.array(W) / sumW)
                    # rand p
                    rand = np.random.rand()
                    index = np.where(P >= rand)[0][0]
                    grayCluster[g[index]] = k
                    g.pop(index)
                    h.pop(index)
            # print(grayCluster)

            # tam cum ban dau
            M = {}
            for e, c in grayCluster.items():
                M[c] = e

            clusters = grayCluster.values()
            euclide = 1e-10
            loops = 0
            while(True):
                loops += 1
                curM = {}
                for c in clusters:
                    curM[c] = {
                        "mean": M[c],
                        "totalSum": M[c],
                        "items": 1
                    }
                for gray in g:
                    k = -1
                    m = 256**2
                    for c in clusters:
                        distance = (int(gray) - int(curM[c]["mean"]))**2
                        if (distance < m):
                            m = distance
                            k = c
                    grayCluster[gray] = k
                    curM[k]["totalSum"] += int(gray)
                    curM[k]["items"] += 1
                    curM[k]["mean"] = curM[k]["totalSum"]/curM[k]["items"]
                stopable = True
                for c in clusters:
                    if abs(M[c] - curM[c]["mean"]) > euclide: 
                        stopable = False
                        break
                for c in clusters:
                    M[c] = curM[c]["mean"]
                if stopable or loops == 100: 
                    break
            print("loops count: ", loops )
            # result
            outImg = np.vectorize(lambda pixel: M[grayCluster[pixel]])(img).astype(img.dtype)

            img_bytes = io.BytesIO()
            # iio.imwrite(img_bytes, img, extension=".png")
            iio.imwrite(img_bytes, outImg, extension=".png")
            img_bytes.seek(0)

            return {"success": True, "bytes": img_bytes, 'clusters': maximumCluster}
        except Exception as e:
            return {"success": False, "message": str(e)}

    @staticmethod    
    def KmeanStandard(imagePath, nCluster):
        try :
            img = iio.imread(imagePath)
            g, h = np.unique(img, return_counts=True)
            g = g.tolist()
            h = h.tolist()
            maximumCluster = len(g)

            # C0
            grayCluster = {}
            for k in range(nCluster):
                cluster = np.random.choice(g)
                grayCluster[cluster] = k
                index = g.index(cluster)
                g.pop(index)
                h.pop(index)

            # tam cum ban dau
            M = {}
            for e, c in grayCluster.items():
                M[c] = e

            clusters = grayCluster.values()
            euclide = 1e-10
            loops = 0
            while(True):
                loops += 1
                curM = {}
                for c in clusters:
                    curM[c] = {
                        "mean": M[c],
                        "totalSum": M[c],
                        "items": 1
                    }
                for gray in g:
                    k = -1
                    m = 256**2
                    for c in clusters:
                        distance = (int(gray) - int(curM[c]["mean"]))**2
                        if (distance < m):
                            m = distance
                            k = c
                    grayCluster[gray] = k
                    curM[k]["totalSum"] += int(gray)
                    curM[k]["items"] += 1
                    curM[k]["mean"] = curM[k]["totalSum"]/curM[k]["items"]
                stopable = True
                for c in clusters:
                    if abs(M[c] - curM[c]["mean"]) > euclide: 
                        stopable = False
                        break
                for c in clusters:
                    M[c] = curM[c]["mean"]
                if stopable or loops == 100: 
                    break
            print("loops count: ", loops )
            # result
            outImg = np.vectorize(lambda pixel: M[grayCluster[pixel]])(img).astype(img.dtype)

            img_bytes = io.BytesIO()
            # iio.imwrite(img_bytes, img, extension=".png")
            iio.imwrite(img_bytes, outImg, extension=".png")
            img_bytes.seek(0)

            return {"success": True, "bytes": img_bytes, 'clusters': maximumCluster}
        except Exception as e:
            return {"success": False, "message": str(e)}

