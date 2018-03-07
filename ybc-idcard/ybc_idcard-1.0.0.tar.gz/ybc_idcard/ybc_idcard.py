from qcloud_image import Client
from qcloud_image import CIUrl, CIFile, CIBuffer, CIUrls, CIFiles, CIBuffers

appid = '1251185167'
secret_id = 'AKIDiFYdT5XeaIl04utt2waz87sOfiY9ucV9'
secret_key = 'XrwmMgkY6OQFvMYVEixxiDSRAdqnUw84'
bucket = 'ocr'
client = Client(appid, secret_id, secret_key, bucket)
client.use_http()
client.set_timeout(30)

def front_info(filename=''):
    '''返回身份证正面信息'''
    if filename == '':
        return -1
    info = client.idcard_detect(CIFiles([filename]), 0)

    res = info['result_list'][0]
    if res['code'] == 0:
        del res['data']['name_confidence_all']
        del res['data']['sex_confidence_all']
        del res['data']['nation_confidence_all']
        del res['data']['birth_confidence_all']
        del res['data']['address_confidence_all']
        del res['data']['id_confidence_all']
        return res['data']
    else:
        return -1

def back_info(filename=''):
    '''返回身份证反面信息'''
    if filename == '':
        return -1
    info = client.idcard_detect(CIFiles([filename]), 1)
    res = info['result_list'][0]
    if res['code'] == 0:
        del res['data']['authority_confidence_all']
        del res['data']['valid_date_confidence_all']
        return res['data']
    else:
        return -1

def idcard_compare(cardnum,name,filename):
    '''信息和证件比对'''
    if cardnum and name and filename:
        info = client.face_idcardcompare(cardnum, name, CIFile(filename))
        res = info['result_list'][0]
        if res['code'] == 0:
            return res['data']
        else:
            return -1
    else:
        return -1
