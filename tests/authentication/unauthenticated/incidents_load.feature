Feature: Incidents and organizations load
    In order to log in
    An Unauthenticated User
    Should be able to choose a username from a dynamic list, based upon the incident
 
    Scenario: Load organization list by incident
        Given I am an Unauthenticated User
        And I visit "/authentication"
        And I choose an Incident from the "Choose Incident" dropdown menu
        Then the the Organization dropdown should appear, populated with a list of at least two organizations (admin and local_admin), and the Passcode field should appear, and a "Login" button should appear