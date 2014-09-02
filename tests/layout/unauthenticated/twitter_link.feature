Feature: Layout link to Twitter is live
    In order to connect visitors with Crisis Cleanup resources
    An Unauthenticated User
    Should be forwarded to the correct link when clicking the "Twitter" icon
    
    Scenario: Unauthenticated User clicks the "Twitter" and the Twitter page loads
        Given I am an Unauthenticated User
        And I visit the page "/home"
        And I click the "Twitter" icon at the top right corner of the page
        Then the page "https://www.twitter.com/crisiscleanup" should load in the current tab