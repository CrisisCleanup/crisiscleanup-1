Feature: Layout link to Public Map is live
    In order to connect visitors with Crisis Cleanup resources
    An Unauthenticated User
    Should be forwarded to the correct link when clicking the "Map" tab
    
    Scenario: Unauthenticated User clicks "Map" and the Public Map page loads
        Given I am an Unauthenticated User
        And I visit the page "/home"
        And I click the "Map" tab
        Then the page "/public-map" should load in the current tab