from webserver import app
import webserver.routes

if __name__ == '__main__':
    app.run(host = '0.0.0.0',port=8080,debug=True)