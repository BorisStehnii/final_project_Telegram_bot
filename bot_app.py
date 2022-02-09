from app import fapp, Config


if __name__ == '__main__':

    fapp.run(debug=True, host=Config.APP_URL)


