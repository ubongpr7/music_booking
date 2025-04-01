
# Music Booking API

## 📌 Overview
The **Music Booking API** is a RESTful API designed for efficient management of artist profiles, event listings, and booking transactions. This API provides a seamless way for users to explore events, book tickets, and manage bookings securely and scalably.

## 🚀 Features
- **Artist Management**: Create, update, and retrieve artist profiles.
- **Event Listings**: Manage events, ticket prices, and availability.
- **Booking System**: Securely handle ticket reservations with unique booking references.
- **Payment Processing**: 
  - Integrated **Stripe** for secure online payments.
  - The system supports a Stripe Checkout session, where users can complete their payments.
  - **Webhook Integration**: Set up your Stripe webhook to listen for events such as payment success or failure.
  - Ability to integrate other payment gateways in the future for more payment options.
- **Admin & User Authentication**: Secure API with authentication and authorization.

## 🏗️ Tech Stack
- **Backend**: Django Rest Framework (DRF), PostgreSQL
- **Authentication**: JWT Authentication
- **Containerization**: Docker & Docker Compose
- **Documentation**: OpenAPI (Swagger) & Postman Collection
- **Testing**: Pytest & Django Test Framework
- **Payment Integration**: Stripe (for payment processing)

## 📂 Installation & Setup
### Prerequisites
- Docker & Docker Compose installed
- Python 3.11+
- PostgreSQL database
- **Stripe Account**: You will need a Stripe account to use the payment gateway.

### Clone the Repository
```bash
git clone https://github.com/ubongpr7/music_booking.git
cd music_booking
```

### Set Up Environment Variables
Create a `.env` file and define the necessary environment variables:
```
EMAIL_HOST_USER=ubongpr7@gmail.com
EMAIL_HOST_PASSWORD=nmcmiwlgwdrwesef
SECRET_KEY=django-insecure-pvc)e7cia$y25l0lc^b@#j+5c628x8+b(^eirvpgk3$z6^t8wh
DEBUG=True
DB_NAME=postgress
DB_USER=postgress
DB_PASSWORD=postgress
DB_HOST=db
DB_PORT=5432
STRIPE_ENDPOINT_SECRET=''
STRIPE_PUP_KEY=''
STRIPE_SEC_KEY=''
```

- **EMAIL_HOST_USER**: Your email address used for sending emails (e.g., registration or password reset).
- **EMAIL_HOST_PASSWORD**: Your email password or app-specific password for authentication.
- **SECRET_KEY**: The secret key used by Django for cryptographic signing.
- **DEBUG**: Set to `True` for development and `False` for production.
- **DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT**: Database connection settings for PostgreSQL.
- **STRIPE_ENDPOINT_SECRET**: Your Stripe webhook secret to validate incoming Stripe events.
- **STRIPE_PUP_KEY**: Your Stripe public key used for client-side Stripe integration.
- **STRIPE_SEC_KEY**: Your Stripe secret key used for server-side Stripe integration.

### Run the Application using Docker
```bash
docker-compose up --build
```


## 📌 API Endpoints
For detailed information on the available API endpoints, refer to the `swagger.json` file located in the root directory. This file contains a complete list of the API endpoints, including request methods, descriptions, and required parameters.

For a full API documentation interface, you can also visit: `http://localhost:7745/swagger/`.

## 📊 Database Schema
The database schema has been generated using **Django Graph Models**. To visualize it, run:
```bash
python manage.py graph_models -a -o schema.png
```
A preview of the database relationships is available in the root directory as `schema.png`.


## 📮 Postman Collection
The API endpoints can be tested using the **Postman collection** provided.
1. Import the `swagger.json` file into Postman.
2. Set the base URL to `http://localhost:7745/`.

## 🔐 Security Measures
- **JWT Authentication**: Secure authentication system.
- **CORS Policies**: Restricts unauthorized access.

## 🛠️ Stripe Integration & Webhook Setup
1. **Stripe Checkout**: The API supports Stripe Checkout for handling ticket payments. When a booking is created, you can generate a Stripe Checkout session to process the payment.
   
2. **Webhook**: 
   - To listen for payment status updates, you need to configure your Stripe Webhook. Ensure that you have added your webhook secret to your environment variables (`STRIPE_ENDPOINT_SECRET`).
   - Use the Stripe API to validate webhook events that are sent to your server, so you can take action based on payment success or failure.

3. **Integrating Other Payment Methods**: If you'd like to integrate additional payment methods, you can extend the payment processing logic to support other gateways alongside Stripe.

## 👨‍💻 Contribution Guidelines
1. Fork the repository.
2. Create a new feature branch: `git checkout -b feature-new-feature`.
3. Commit your changes: `git commit -m 'Add new feature'`.
4. Push to the branch: `git push origin feature-new-feature`.
5. Open a Pull Request.

## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
💡 **Need help?** Open an issue or contact the maintainer at [ubongpr7@gmail.com](mailto:ubongpr7@gmail.com).

---
