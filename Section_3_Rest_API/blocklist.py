"""blocklist.py
This file just contains the blocklist set to store the JWTs that we want to revoke. This is imported by the app and the logout resource so that the token can be added to the blocklist on logout and checked against the blocklist when the user logs out.
"""

BLOCKLIST = set()