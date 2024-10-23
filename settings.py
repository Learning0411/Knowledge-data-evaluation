import os


class BaseConfig(object):
    DEBUG = True
    SECRET_KEY = os.getenv('SECRET_KEY',
                           '\xfe&\xa2\x1d\xd1bZ\xe2\xf9iu\xab\xbd\xd8\xf98\xf2a"5\xf9vNU')
    MONGO_URI = "mongodb://localhost:27017/DataMap"
    # 上传最大文件
    MAX_CONTENT_LENGTH = 3 * 1024 * 1024
    FILE_LIMITS = ['txt']

class DevelopmentConfig(BaseConfig):
    MONGO_URI = "mongodb://localhost:27017/DataMap"

config = {
    'development': DevelopmentConfig,
}
