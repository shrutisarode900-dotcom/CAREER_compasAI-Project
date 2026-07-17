from career_compass import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=(app.config.get("FLASK_ENV") != "production"))


