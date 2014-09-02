Feature: /authentication automatically forwards to assessment form when logged in
    In order to avoid confusion when a user is already logged in
    An Authenticated Admin
    Should be forwarded directly to the page "/" and the assessment form when visiting "/authentication"
 
    Scenario: Forward if already logged in
        Given I am an Authenticated Admin
        And I visit "/authentication"
        Then I am forwarded to the page "/" and the words, "Organization: Admin" appear at the top left of the page, and the words "(Admin Panel)" appear at the top left of the page, hyperlinked to "/admin", and the assessment form loads.