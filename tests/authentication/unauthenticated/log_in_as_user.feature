Feature: Log in as user
    In order to log in as a user
    An Unauthenticated User
    Should be able to choose username from a dynamic list, based upon the incident, enter a password, and log in.
 
    Scenario: Log in as a user
        Given I am an Unauthenticated User
        And I visit "/authentication"
        And I choose a valid incident from the "Choose Incident" dropdown menu
        And I choose a user that is not "Admin" and does not begin with "Local Admin" from the "Organization" dropdown menu
        And I enter a valid passcode in the "Passcode" field
        And I click "Login"
        Then I am forwarded to the page "/" and the words, "Organization:" appear at the top left of the page, and the assessment form loads.