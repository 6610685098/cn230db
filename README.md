# CN230 Project: Formula 1 Bahrain Grand Prix 2024 Data Analysis

### Objective
* Fetches real-time Formula 1 race data using a public API.
* Stores the data in a relational database (SQLite).
* Performs analytical queries to extract insights such as top drivers, team performance, and qualifying statistics.
  
### Tools
Language: Python	

Library: Requests, SQLite3	

Source: Ergast API [https://ergast.com/mrd/]

API Endpoints:  
1. Driver Standings [http://ergast.com/api/f1/2024/1/driverStandings.json]
2. Constructor Standings [https://ergast.com/api/f1/2024/1/constructorStandings.json]
3. Qualifying Results [http://ergast.com/api/f1/2024/1/qualifying.json]

### How It Works
#### 1. Fetching Data from APIs
The system accesses three REST API endpoints to retrieve JSON data for the current race:

* Driver standings

* Constructor standings

* Qualifying session results (Q1, Q2, Q3 lap times)

The function \*fetch_data(url)\* sends HTTP GET requests and parses the JSON response.

#### 2. Setting Up the Database Schema
The SQLite database is initialized with four tables:

* drivers: Stores driver details (id, name, nationality, constructor)

* standings: Driver race standings (position, points, wins)

* constructor_standings: Constructor team standings (position, points, wins)

* qualifying_results: Qualifying session times and positions

#### 3. Inserting Data into Database
Data parsed from API responses is inserted into the respective tables:

* Drivers and their standings go into drivers and standings.

* Constructors and their rankings go into constructor_standings.

* Qualifying times (Q1, Q2, Q3) and best lap times go into qualifying_results.


### Database Design
#### Table: `drivers`

| Column       | Type   | Description                              |
|--------------|--------|------------------------------------------|
| `driverId`   | TEXT   | Primary key (unique driver identifier)   |
| `givenName`  | TEXT   | Driver's first name                      |
| `familyName` | TEXT   | Driver's last name                       |
| `nationality`| TEXT   | Driver's nationality                     |
| `constructor`| TEXT   | Name of the constructor team             |

#### Table: `standings`

| Column     | Type    | Description                              |
|------------|---------|------------------------------------------|
| `driverId` | TEXT    | Foreign key referencing `drivers`        |
| `position` | INTEGER | Driver’s rank in the standings           |
| `points`   | REAL    | Total championship points                |
| `wins`     | INTEGER | Number of wins                           |

#### Table: `constructor_standings`

| Column         | Type    | Description                            |
|----------------|---------|----------------------------------------|
| `constructorId`| TEXT    | Primary key (unique team identifier)   |
| `name`         | TEXT    | Name of the constructor team           |
| `nationality`  | TEXT    | Team nationality                       |
| `position`     | INTEGER | Team's rank in the championship        |
| `points`       | REAL    | Total points earned by the team        |
| `wins`         | INTEGER | Number of team wins                    |

#### Table: `qualifying_results`

| Column      | Type    | Description                                  |
|-------------|---------|----------------------------------------------|
| `driverId`  | TEXT    | Foreign key referencing `drivers`            |
| `position`  | INTEGER | Starting grid position after qualifying      |
| `best_time` | REAL    | Fastest qualifying lap time (in seconds)     |
| `Q1`        | TEXT    | Lap time during Q1 session (as string)       |
| `Q2`        | TEXT    | Lap time during Q2 session (as string)       |
| `Q3`        | TEXT    | Lap time during Q3 session (as string)       |

### Features & Analytics

* Driver
  * Top 5 drivers by points
  * Fastest Qualifying lap \* This statistic is not based on the qualifying rank (grid position), but rather calculated independently by comparing the fastest lap time across all qualifying sessions (Q1, Q2, Q3) for each driver. \*
  * Top 10 Qualifiers  
  * Average points 

* Constructor
  * Top 5 constructors by points
  * First place
  * Last place

 ### Summary
This project demonstrates how to:

* Collect real-time sports data via public APIs

* Design and implement a relational database schema

* Process and store complex nested JSON data

* Perform analytical queries to extract insights such as top drivers, average points, and fastest qualifying laps
