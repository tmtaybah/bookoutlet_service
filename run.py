from bookoutlet_service import app

THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED     = True

if __name__ == '__main__':
    app.run(debug=True)
