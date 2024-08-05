# Online Imtiaz Mart API

## Project Overview

This project involves developing an online mart API using an event-driven microservices architecture. The API is designed to be scalable, maintainable, and efficient, capable of handling high volumes of transactions and data in a distributed manner. 

The system leverages several modern technologies and practices to achieve these goals:

- **FastAPI** for high-performance API development
- **Docker** for containerization
- **Docker Compose** for orchestrating multi-container applications
- **PostgreSQL** for data persistence
- **Kafka** for event streaming
- **Kong** for API gateway management
- **GitHub Actions** for continuous integration and continuous deployment (CI/CD)
- **Test-Driven Development (TDD)** with **Pytest** for ensuring code quality

## Objectives

- Develop a scalable and efficient API for an online mart using microservices.
- Implement an event-driven architecture to handle asynchronous communication between services.
- Use FastAPI for API development and Docker for containerization.
- Ensure smooth development and deployment with Docker Compose.
- Manage and route API requests through Kong API Gateway.
- Persist data using PostgreSQL.
- Incorporate TDD to enhance code quality and ensure the application meets business requirements.

## Technologies

- **FastAPI**: A modern, fast (high-performance) web framework for building APIs with Python.
- **Docker**: Containerizes the microservices to ensure consistency across different environments.
- **Docker Compose**: Orchestrates multi-container Docker applications.
- **PostgreSQL**: A powerful, open-source relational database system.
- **SQLModel**: Interacts with the PostgreSQL database using Python.
- **Kafka**: A distributed event streaming platform for building real-time data pipelines and streaming applications.
- **Kong**: An open-source API Gateway and Microservices Management Layer.
- **GitHub Actions**: For CI/CD pipeline.
- **Pytest**: For unit testing and TDD.

## Architecture

### Microservices

- **User Service**: Manages user authentication, registration, and profiles.
- **Product Service**: Manages the product catalog, including CRUD operations for products.
- **Order Service**: Handles order creation, updating, and tracking.
- **Inventory Service**: Manages stock levels and inventory updates.
- **Notification Service**: Sends notifications (email, SMS) to users about order statuses and other updates.
- **Payment Service**: Processes payments and manages transaction records. Note: We will use Pay Fast for local payments and Stripe for international payments.

### Event-Driven Communication

- **Kafka**: Acts as the event bus, facilitating communication between microservices. Each service can produce and consume messages (events) such as user registration, order placement, and inventory updates.

### Data Storage

- **PostgreSQL**: Each microservice with data persistence needs will have its own PostgreSQL database instance, following the database-per-service pattern.

### API Gateway

- **Kong**: Manages API request routing, authentication, rate limiting, and other cross-cutting concerns.

### Development Environment

- **DevContainers**: Provides consistent development environments using VSCode DevContainers, ensuring that all team members work in identical environments.
- **Docker Compose**: Orchestrates the various microservices and dependencies (PostgreSQL, Kafka, etc.) during development and testing.

## Development Methodologies

### Test-Driven Development (TDD)

TDD involves writing tests before writing the actual code. This ensures that the code meets the required functionality and helps prevent bugs. In this project, Pytest will be used for unit testing.

## Implementation Plan

### Phase 1: Setup and Initial Development

1. **Setup Development Environment**
   - Configure DevContainers with necessary dependencies and tools.
   - Create Docker Compose file for orchestrating services and dependencies.

2. **Develop Microservices with TDD**
   - Implement the User Service, Product Service, Order Service, Payment Service, and Notification Service using FastAPI and SQLModel.
   - Write unit tests using Pytest before writing the actual code.
   - Containerize each microservice using Docker.

3. **Setup Kafka**
   - Configure Kafka for event streaming.

### Phase 2: Expand Functionality

1. **Develop Additional Microservices**
   - **Inventory Service**: Manage stock levels and inventory updates.
   - **Notification Service**: Send notifications about order statuses and other events.
   - **Payment Service**: Process payments and manage transactions.

2. **Integrate Event-Driven Communication**
   - Ensure all services can produce and consume relevant Kafka messages.

### Phase 3: Implement API Gateway and Finalize

1. **Setup Kong API Gateway**
   - Configure Kong for routing, authentication, and rate limiting.
   - Create routes for each microservice.

2. **Testing and Quality Assurance**
   - Write unit, integration, and end-to-end tests for all services.
   - Perform load testing to ensure scalability and performance.

### Phase 4: Monitoring and Continuous Delivery (Optional)

1. **Implement Monitoring and Logging**
   - Set up monitoring tools (e.g., Prometheus, Grafana) to track service health and performance.
   - Implement centralized logging for troubleshooting and analysis.

2. **Continuous Delivery with GitHub Actions**
   - Use GitHub Actions to continuously deliver code for deployment to the cloud.

## Points to Note

- Use SQLModel to communicate with PostgreSQL database.
- Docker Compose up should create all necessary services.
- GitHub Actions will handle deployment automation.

## Conclusion

This project aims to create a robust, scalable, and efficient online mart API using an event-driven microservices architecture. By leveraging technologies such as FastAPI, Docker, Kafka, PostgreSQL, and Kong, the project ensures a high-performance and maintainable system capable of handling large-scale operations. The development will follow a phased approach, ensuring thorough testing, quality assurance, and continuous improvement.
