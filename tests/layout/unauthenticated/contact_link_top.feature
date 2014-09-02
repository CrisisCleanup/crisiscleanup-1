Feature: Layout link to Contact is live
    In order to connect visitors with Crisis Cleanup resources
    An Unauthenticated User
    Should be forwarded to the correct link when clicking the "Contact" icon
    
    Scenario: Unauthenticated User clicks the "Contact" icon and the Contact page loads
        Given I am an Unauthenticated User
        And I visit the page "/home"
        And I click the "Contact" icon at the top right corner of the page
        Then the page "/contact" should load in the current tab