Feature: Layout link to Login is live
    In order to connect visitors with Crisis Cleanup resources
    An Unauthenticated User
    Should be forwarded to the correct link when clicking the "Log In" tab
    
    Scenario: Unauthenticated User clicks "Log In" and the Login page loads
        Given I am an Unauthenticated User
        And I visit the page "/home"
        And I click the "Log In" tab
        Then the page "/authentication" should load in the current tab