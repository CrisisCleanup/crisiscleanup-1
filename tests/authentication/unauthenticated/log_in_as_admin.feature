Feature: Log in as admin
    In order to log in as an administrator
    An Unauthenticated User
    Should be able to choose a the "admin" username from a dynamic list, based upon the incident, enter a password, and log in.
 
    Scenario: Log in as admin
        Given I am an Unauthenticated User
        And I visit "/authentication"
        And I choose a valid incident from the "Choose Incident" dropdown menu
        And I choose the user "Admin" from the "Organization" dropdown menu
        And I enter a valid passcode in the "Passcode" field
        And I click "Login"
        Then I am forwarded to the page "/" and the words, "Organization: Admin" appear at the top left of the page, and the words "(Admin Panel)" appear at the top left of the page, hyperlinked to "/admin" and the assessment form loads.