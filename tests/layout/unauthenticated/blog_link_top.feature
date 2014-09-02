Feature: Layout link to the Blog is live
    In order to connect visitors with Crisis Cleanup resources
    An Unauthenticated User
    Should be forwarded to the correct link when clicking the "Blog" tab
    
    Scenario: Unauthenticated User clicks "Blog" and the Blog page loads
        Given I am an Unauthenticated User
        And I visit the page "/home"
        And I click the "Blog" tab
        Then the page "http://blog.crisiscleanup.org/" should load in the current tab