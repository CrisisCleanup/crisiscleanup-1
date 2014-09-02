Feature: Layout link to Facebook is live
    In order to connect visitors with Crisis Cleanup resources
    An Unauthenticated User
    Should be forwarded to the correct link when clicking the "Facebook" icon
    
    Scenario: Unauthenticated User clicks the "Facebook" and the Facebook page loads
        Given I am an Unauthenticated User
        And I visit the page "/home"
        And I click the "Facebook" icon at the top right corner of the page
        Then the page "https://www.facebook.com/pages/Crisis-Cleanup/437690172982553?fref=ts" should load in the current tab