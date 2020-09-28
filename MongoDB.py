# create connection and connect to the database
from mongoengine import connect, Document, fields


# create a user class
class User_Map(Document):
    meta = {"collection": "container"}  # db 밑에 컬렉션 생성
    username = fields.StringField(required=True)
    profile_image = fields.ImageField(thumbnail_size=(150,150,False))

class User_OTP_T(Document):
    username = fields.StringField(required=True)
    meta = {"collection": "otp_result"}  # db 밑에 컬렉션 생성
    text = fields.StringField(max_length=100)


class User_OTP_P(Document):
    username = fields.StringField(required=True)
    meta = {"collection": "otp_intruder"}  # db 밑에 컬렉션 생성
    profile_image = fields.ImageField(thumbnail_size=(150,150,False))



class MongoDB:
    def __init__(self):
        # '192.168.0.15'
        connect(db="Hobserver", host='localhost', port=27017)  # 데이터 베이스생성  -> 컬렉션

    # 저장할 이미지를 매개변수로 넣으면 바로 저장
    def storeImg_map(self, img=None, filename=None):
        kobot_B = User_Map(username='kobot_B')  # User_Map 객체 생성 : 실시간 도출된 맵 반영
        kobot_B.profile_image.replace(img, filename=filename)
        kobot_B.save()

    def storeImg_otp(self, img=None, filename=None):
        kobot_B = User_OTP_P(username='kobot_B')  # User_OTP_P 객체 생성 : 침입자의 모습 저장
        kobot_B.profile_image.replace(img, filename=filename)
        kobot_B.save()

    def storeStr_otp(self, word=None):
        kobot_B = User_OTP_T(username='kobot_B')  # User_OTP 객체 생성 : 실시간 otp 결과 반영
        kobot_B.text = word
        kobot_B.save()

if __name__ =='__main__':
    mongo = MongoDB()
    mongo.storeImg_otp()