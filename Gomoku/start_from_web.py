from Web import web_start, app

try:
    # web_start.socket_io.run(app, host='0.0.0.0')
    app.run()
except KeyboardInterrupt:
    web_start.disconnect()
    #web_start.socket_io.stop()
