from app import create_app

if __name__ == "__main__":
    app = create_app()
    
    app.run(host = LOCALHOST, port = 5000)