Feature: Layout link to LINK is live
    In order to connect visitors with Crisis Cleanup resources
    An Unauthenticated User
    Should be forwarded to the correct link when clicking the "Sign Up" tab
    
    Scenario: Unauthenticated User clicks "Sign Up" and the Sign Up page loads
        Given I am an Unauthenticated User
        And I visit the page "/home"
        And I click the "Sign Up" tab
        Then the page "/signup" should load in the current tab in the current tab