# Rental Marketplace Web Application

A Flask-based rental marketplace where users can list items for rent and rent items from other users.

## Features

- **User Authentication**: Registration and login system
- **Item Management**: Upload items with images, categories, and pricing
- **Rental Booking**: Book items for selected date ranges
- **Payment Placeholder**: Payment processing simulation
- **Dashboard**: Separate views for owners and renters
- **RESTful APIs**: Complete API endpoints for frontend integration

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: HTML, Bootstrap 5, JavaScript
- **Authentication**: Flask-Login

## Project Structure

```
kaarya_satu/
├── app/
│   ├── __init__.py          # Flask app initialization
│   ├── models.py            # Database models
│   ├── routes.py             # Main routes (HTML templates)
│   ├── auth.py               # Authentication routes
│   └── api.py                # REST API endpoints
├── templates/
│   ├── base.html             # Base template
│   ├── index.html            # Home page
│   ├── login.html            # Login page
│   ├── register.html         # Registration page
│   ├── items.html            # Browse items page
│   ├── item_detail.html      # Item details page
│   └── dashboard.html        # User dashboard
├── static/                   # CSS, JS, images (if needed)
├── uploads/                  # Uploaded item images
├── app.py                    # Application entry point
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Installation

1. **Clone the repository** (or navigate to the project directory)

2. **Create a virtual environment** (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Run the application**:
```bash
python app.py
```

5. **Access the application**:
   - Open your browser and navigate to `http://localhost:5000`

## Database Schema

The application uses SQLite with the following main tables:

- **User**: Stores user account information
- **Item**: Stores rental items with details
- **Rental**: Stores rental bookings
- **Payment**: Stores payment transactions

See `ER_DIAGRAM.md` for detailed entity relationship diagram.

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `GET /auth/logout` - User logout

### Items
- `GET /api/items` - Get all items (with optional filters)
- `GET /api/items/<id>` - Get specific item
- `POST /api/items` - Create new item (requires auth)
- `PUT /api/items/<id>` - Update item (owner only)
- `DELETE /api/items/<id>` - Delete item (owner only)

### Rentals
- `GET /api/rentals` - Get user's rentals
- `GET /api/rentals/<id>` - Get specific rental
- `POST /api/rentals` - Create rental booking
- `PUT /api/rentals/<id>/status` - Update rental status (owner only)

### Payments
- `POST /api/payments` - Process payment (placeholder)
- `GET /api/payments/<id>` - Get payment details

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics

## Usage

1. **Register/Login**: Create an account or login
2. **List Items**: Go to dashboard and click "List New Item"
3. **Browse Items**: View available items on the home page or browse page
4. **Rent Items**: Click on an item and select dates to book
5. **Manage Rentals**: View and manage rentals in the dashboard

## Notes

- Payment processing is a placeholder - transactions are automatically marked as completed
- Images are stored in the `uploads/` directory
- The database file (`rental_marketplace.db`) is created automatically on first run
- Change the `SECRET_KEY` in production

## License

This project is for educational purposes.

