# IMTDB MIXTE

## Overview
This project implements a cinema management system with four microservices: Movie, Booking, Times, and User. This time, some APIs will be written using GraphQL and gRPC, resulting in a mixed API application.

### Install Dependencies
Make sure to install the required dependencies:

```bash
pip install -r requirements.txt
```

Major Changes
-**Movie Service Migration to GraphQL**: Rewrote the Movie service to utilize GraphQL for data retrieval. Updated the User service to make GraphQL queries instead of REST calls.

-**User Service Modification**: Adapted the User service to send GraphQL requests to the Movie service using the POST method, ensuring compatibility with the new API.

-**Times Microservice Development with gRPC**: Created API proto files for the Times service and implemented the service using gRPC. 

-**Booking Microservice Implementation with gRPC**: Developed the Booking service using gRPC by creating the necessary API proto files. Updated the service to replace REST requests to Times with gRPC remote procedure calls, making Booking both a gRPC server and client.

-**User Service Integration with gRPC**: Modified the User service to replace REST requests to Booking with gRPC calls, maintaining its functionality as a REST server while integrating gRPC communication.
