import botocore
import boto3, base64, cv2
import numpy as np

s3Client = boto3.client("s3")

def sendBase64ImageToS3(bucketName, key, base64Code):
    try:
        img_bytes = base64.b64decode(base64Code)
        s3Client.put_object(Bucket=bucketName, Key=key, Body=img_bytes)
    except botocore.exceptions.ClientError as err:
        print("Err to send File to S3:", err)
        raise

def downloadFileFromS3(bucketName, key, destFile):
    try:
        s3Client.download_file(bucketName, key, destFile)
    except botocore.exceptions.ClientError as err:
        if err.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise
        return 0
    return destFile

def convertBytesImageIntoOpenCVImage(bytesImage):
    img_bytes = base64.b64decode(bytesImage)
    nparr = np.asarray(bytearray(img_bytes), dtype=np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img


def convertBytesImageIntoBase64Image(img, img_typ):
    if img_typ == 'image/png':
        tpye = '.png'
    elif img_typ == 'image/jpg' or img_typ == 'image/jpeg':
        tpye = '.jpg'
    else:
        return ""

    retval, buffer = cv2.imencode(tpye, img)
    base64_code = base64.b64encode(buffer)
    base64_code = 'data:'+img_typ+';base64,' + base64_code.decode('ascii')

    return base64_code
