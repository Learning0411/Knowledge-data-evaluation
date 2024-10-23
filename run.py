# import sys
# sys.path.append("..")
from init import create_app




app = create_app()
app.run(host='127.0.0.1', port=8008, debug=True)


# if __name__ == '__main__':
#     run_app()
