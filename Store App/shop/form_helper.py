from werkzeug.utils import secure_filename
import os

class FormHelper():
    def __init__(self, upload_folder, allowed_extensions):
        self.UPLOAD_FOLDER = upload_folder
        self.ALLOWED_EXTENSIONS = allowed_extensions
    
    def allowed_file(self, filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS

    def upload_file(self, file):
        # If valid file it stores it and returns the stored
        # location and otherwise returns None
        if file.filename == '':
            print("Empty file name")
            return None
        if file and self.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            #print("filelocal", os.path.join(self.UPLOAD_FOLDER, filename))
            location = os.path.join(self.UPLOAD_FOLDER, filename)
            file.save(location)
            return filename


