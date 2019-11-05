from flask import Flask,request,render_template
from ocr import invoiceocr

app=Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/result',methods=['GET','POST'])
def result():
    if request.method=='POST':
        file=request.files.get('myfile')
        data1,data2,data3,data4,data5=invoiceocr(file)
        
        return render_template('result.html',data1=data1,data2=data2,data3=data3,data4=data4,data5=data5)

if __name__=='__main__':
    app.run()
