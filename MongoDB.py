# create connection and connect to the database
from mongoengine import connect, Document, fields
# connect(db="Hobserver", host="localhost", port=27017) # 데이터 베이스생성  -> 컬렉션
#
#
# # create a user class
# class User(Document):
#     meta = {"collection": "container"}  # db 밑에 컬렉션 생성
#     username = fields.StringField(required=True)
#     profile_image = fields.ImageField(thumbnail_size=(150,150,False))
#
#
# # create a user object, uploads image and save
# conny = User(username = 'map')
# my_image = open('./container/17.jpg', 'rb')
# conny.profile_image.replace(my_image, filename='map.jpg')
# conny.save()
#
# # retrieve the image
# user = User.objects(username="map").first()
# user.profile_image.read()
#
# #################################################################


# create a user class
class User(Document):
    meta = {"collection": "container"}  # db 밑에 컬렉션 생성
    username = fields.StringField(required=True)
    profile_image = fields.ImageField(thumbnail_size=(150,150,False))

class MongoDB:
    def __init__(self, dbName=None):

        connect(db=dbName, host="localhost", port=27017)  # 데이터 베이스생성  -> 컬렉션
        self.conny = User(username='map')  # User 객체 생성


    # 저장할 이미지를 매개변수로 넣으면 바로 저장
    def storeImg(self, img=None):
        self.conny.profile_image.replace(img, filename='map.jpg')
        self.conny.save()

    # 이미지 가져오기
    def retrieveIme(self):
        # retrieve the image
        user = User.objects(username="map").first()
        user.profile_image.read()


if __name__ =='__main__':
    mongo = MongoDB('Hobserver')
    mongo.storeImg()