Feature: Layout link to Donate is live
    In order to connect visitors with Crisis Cleanup resources
    An Unauthenticated User
    Should be forwarded to the correct link when clicking the "Donate" button
    
    Scenario: Unauthenticated User clicks the orange "Donate" and the Donate page loads
        Given I am an Unauthenticated User
        And I visit the page "/home"
        And I click the orange "Donate" button
        Then the page "/donate" should load in the current tab