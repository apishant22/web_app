from flask import Flask, render_template, request, redirect, url_for
from scrape_dresses import get_dress_data  # Make sure this function is defined

app = Flask(__name__)

# Number of dresses to display per page
ITEMS_PER_PAGE = 6

# Home route
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get the search query from the form
        user_query = request.form.get('query')
        # Redirect to the results page with the query as a URL parameter
        return redirect(url_for('results', query=user_query, page=1))

    # GET request will render the index.html page
    return render_template('index.html')

# Results route: only handles GET requests
@app.route('/results', methods=['GET', 'POST'])
def results():
    if request.method == 'POST':
        # When user searches again from the results page
        user_query = request.form.get('query')
        return redirect(url_for('results', query=user_query, page=1))

    # Handle GET requests for pagination or initial search
    user_query = request.args.get('query')  # Get query from URL parameters
    page = request.args.get('page', 1, type=int)  # Get current page number

    if not user_query:  # If no query is present, redirect back to homepage
        return redirect(url_for('index'))

    # Fetch dresses based on the search query
    dresses = get_dress_data(user_query)

    # Pagination logic
    total_pages = (len(dresses) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE  # Calculate total pages
    start = (page - 1) * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    dresses_on_page = dresses[start:end]  # Get the dresses for the current page

    return render_template(
        'results.html',
        dresses=dresses_on_page,
        query=user_query,
        page=page,
        total_pages=total_pages,
        max=max,
        min=min
    )

if __name__ == '__main__':
    app.run(debug=True)
