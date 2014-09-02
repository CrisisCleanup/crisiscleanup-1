Feature: Layout link to About is live
    In order to connect visitors with Crisis Cleanup resources
    An Unauthenticated User
    Should be forwarded to the correct link when clicking the "About" tab
    
    Scenario: Unauthenticated User clicks "About" and the About page loads
        Given I am an Unauthenticated User
        And I visit the page "/home"
        And I click the "About" tab
        Then the page "/about" should load in the current tab