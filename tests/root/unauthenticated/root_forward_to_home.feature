Feature: Forward unauthenticated visitor to /home
    In order to avoid an authentication error
    An Unauthenticated User
    Should be forwarded to /home when visiting /
    
    Scenario: Unauthenticated User is forwarded to /home
        Given I am an Unauthenticated User
        And I visit the page "/"
        Then I am forwarded to the page "/home"