from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def hello_world():
  return render_template('index.html')

@app.route('/uploader', methods=['GET', 'POST'])
def file_input():
  if request.method == 'POST':
    file = request.files['file']
    # Do something with the file
    return 'File uploaded successfully'
  return render_template('upload.html')

if __name__ == '__main__':
  app.run(debug=True)
