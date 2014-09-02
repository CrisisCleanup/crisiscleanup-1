Feature: /authentication automatically forwards to assessment form when logged in
    In order to avoid confusion when a user is already logged in
    An Authenticated User
    Should be forwarded directly to the page "/" and the assessment form when visiting "/authentication"
 
    Scenario: Forward if already logged in
        Given I am an Authenticated Admin
        And I visit "/authentication"
        Then I am forwarded to the page "/" and the word, "Organization:" appear at the top left of the page, and the word "(Admin Panel)" does NOT appear at the top left of the page, and the assessment form loads.