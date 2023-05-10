# Queue Monitoring Backend

This repository contains the code for a .NET 7 web application that manages products and checkout history using the ASP.NET Core framework.

## Overview

The application sets up various services such as Swagger for API documentation and a `PostgreSqlService` for database access. It also sets up several API endpoints for managing products and checkout history.

A `TimedHostedService` class is responsible for periodically generating and updating data in the database. It uses a `Timer` to trigger the data generation at regular intervals.

A `DataGenerator` class is used by the `TimedHostedService` to generate data. This class has methods for generating customers based on the current time and store traffic information. It also has methods for checking if the current time is a peak time or low traffic time.

## Getting Started

To run this application, you will need to have the following dependencies installed:

- .NET 7 SDK
- PostgreSQL database

You will also need to set up the necessary configuration values for connecting to the database.

Once you have the dependencies installed and the configuration set up, you can run the application using the `dotnet run` command.