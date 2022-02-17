from webserver import app,db
import webserver.routes

if __name__ == '__main__':
    db.create_all()
    app.run(host = '0.0.0.0',port=8080,debug=True)