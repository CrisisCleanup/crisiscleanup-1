Feature: Layout link to Donate properly forwards
    In order to connect visitors with Crisis Cleanup resources
    An Unauthenticated User
    Should be forwarded to the correct link when clicking the "Donate" button
    
    Scenario: Unauthenticated User visits "/donate" and is forwarded to third party site
        Given I am an Unauthenticated User
        And I visit the page "/donate"
        Then the page automatically forwards to "https://www.crowdrise.com/CrisisCleanup" in the current tab