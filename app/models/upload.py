from db import mongo
import gridfs

class UploadModel:
    def __init__(self, file):
        self.file = file

    def save_file_to_db(self):
        file = self.file
        return mongo.save_file(file.filename, file)

    @classmethod
    def send_file_from_mongo(cls, file_id):
        fs = gridfs.GridFS(mongo.db)
        file = fs.get(file_id)
        return file
