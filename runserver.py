from application import app

if __name__ == '__main__':
    # app.debug = True
    # listen on all public IPs
    app.run(host='0.0.0.0')
#    app.run()
