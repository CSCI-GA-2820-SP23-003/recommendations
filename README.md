# NYU DevOps Project - Recommendation

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)

[![Build Status](https://github.com/CSCI-GA-2820-SP23-003/recommendations/actions/workflows/tdd.yml/badge.svg)](https://github.com/CSCI-GA-2820-SP23-003/recommendations/actions)
[![codecov](https://codecov.io/gh/CSCI-GA-2820-SP23-003/recommendations/branch/master/graph/badge.svg?token=MVEA3AV9VJ)](https://codecov.io/gh/CSCI-GA-2820-SP23-003/recommendations)


## Overview

This project is the implementation of the Recommendation service. The `/service` folder contains the `models.py` file for the model and a `routes.py` file for the service. The `/tests` folder has test case starter code for testing the model and the service separately.

## APIs
```
== Get the list of all recommendations
GET /recommendations
    -> 200 + [Recommendation{}, ...]
    
== Get a recommendation
GET /recommendations/<pid>
    <- Path arg:
            pid : int ; product ID
    -> 200 + Recommendation{}
    
== Create a Recommendation
POST /recommendations
    <- Req JSON:
            pid : int ; product ID
            recommended_pid : int: the recommended product ID
            type : int ; recommendation type
    -> 201 + Recommendation{}
    
== Update a recommendation
PUT /recommendations/<pid>
    <- Path arg:
            pid : int ; product ID
    <- Req JSON:
            pid : int ; product ID
            recommended_pid : int: the recommended product ID
            type : int ; recommendation type
    -> 200 + Recommendation{}
    
== Delete a recommendation
DELETE /recommendations/<pid>
    <- Path arg:
            pid : int ; product ID
    -> 204 + EMPTY

== Like/unlike a recommendation
PUT /recommendations/<pid>/like
PUT /recommendations/<pid>/unlike
    <- Path arg:
            pid : int ; product ID
    -> 200 + Recommendation{}
```

## Manual Setup

You can also clone this repository and then copy and paste the starter code into your project repo folder on your local computer. Be careful not to copy over your own `README.md` file so be selective in what you copy.

There are 4 hidden files that you will need to copy manually if you use the Mac Finder or Windows Explorer to copy files from this folder into your repo folder.

These should be copied using a bash shell as follows:

```bash
    cp .gitignore  ../<your_repo_folder>/
    cp .flaskenv ../<your_repo_folder>/
    cp .gitattributes ../<your_repo_folder>/
```

## Contents

The project contains the following:

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
requirements.txt    - list if Python libraries required by your code
config.py           - configuration parameters

service/                   - service python package
├── __init__.py            - package initializer
├── models.py              - module with business models
├── routes.py              - module with service routes
└── common                 - common code package
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants

tests/              - test cases package
├── __init__.py     - package initializer
├── test_models.py  - test suite for business models
└── test_routes.py  - test suite for service routes
```

## License

Copyright (c) John Rofrano. All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the NYU masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by *John Rofrano*, Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
