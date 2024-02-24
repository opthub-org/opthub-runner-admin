"""
    OptHub API

    OptHub is a \"collaborative optimization\" website that provides a platform
    for socially hosting, analyzing, and solving black-box optimization
    problems. On this site, a user host a competition in which other users join
    to solve problems provided by the host user.
    This API provides basic CRUD operations (create, read, update, delete) to
    run competitions.

    How to run a competition
    ========================
    Organizers:
    1. Create a user.
    2. Create problems.
    3. Create indicators.
    4. Create a competition.
    5. Create matches.

    Participants:
    1. Create a user.
    2. Create a player.
    3. Create a trial.
    4. Create solutions.

    Authorization model
    ===================
    Roles:
    - guest: Everyone without account.
    - user: Everyone with account.
    - owner: The user who created an object to access.
    - admin: System administrators.

    Permission:
    | Object      | guest | user  | owner | admin |
    |-------------|-------|-------|-------|-------|
    | User        | CR    | CR    | CRU   | CRUD  |
    | Problem     |  R    | CR    | CRU   | CRUD  |
    | Indicator   |  R    | CR    | CRU   | CRUD  |
    | Competition |  R    | CR    | CRU   | CRUD  |
    | Match       |  R    | CR    | CRU   | CRUD  |
    | Solution    |  r    | cr    | cR    | CRUD  |

    - C: Create an object anytime.
    - R: Read an object anytime.
    - U: Update an object anytime.
    - D: Delete an object anytime.
    - c: Create an object in the competition period.
    - r: Read an object after the competition period.

    Contact: hmkz@s101.xrea.com
"""

__version__ = "0.8.1"
