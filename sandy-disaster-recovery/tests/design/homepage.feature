Feature: Check that all public pages load
  Scenario: Make sure the site's main page loads
    Given I go to "http://localhost:8080"
      Then I should see "CrisisCleanup"
