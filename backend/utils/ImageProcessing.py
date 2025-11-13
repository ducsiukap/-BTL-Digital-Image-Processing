import imageio.v3 as iio
import io 
import numpy as np

class ImageProcessing: 
    @staticmethod
    def threshold_otsu(imagePath):
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
            outImg = (img <= otsuThreshold).astype(np.uint8)*255

            img_bytes = io.BytesIO()
            # iio.imwrite(img_bytes, img, extension=".png")
            iio.imwrite(img_bytes, outImg, extension=".png")
            img_bytes.seek(0)

            return {"success": True, "bytes": img_bytes}
        except FileNotFoundError as e:
            return {"success": False, "message": str(e)}

