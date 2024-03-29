Feature: The Recommendation API service back-end
    As a Recommendation Service Owner
    I need a RESTful API service
    So that I can keep track of all the product recommendation information

Background:
    Given the following recommendations
        | pid     | recommended_pid | type                  | liked  |
        | 100     | 101             | up-sell               | False  |
        | 100     | 102             | cross-sell            | True   |
        | 200     | 201             | cross-sell            | False  |
        | 300     | 301             | frequently-together   | False  |
        | 400     | 401             | accessory             | True   |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Recommendation RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create a Recommendation
    When I visit the "Home Page"
    And I set the "Product ID" to "1000"
    And I set the "Recommended product ID" to "1001"
    And I select "Up sell" in the "Type" dropdown
    And I select "True" in the "Liked" dropdown
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Recommendation ID" field
    And I press the "Clear" button
    Then the "Recommendation ID" field should be empty
    And the "Product ID" field should be empty
    And the "Recommended product ID" field should be empty
    When I paste the "Recommendation ID" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "1000" in the "Product ID" field
    And I should see "1001" in the "Recommended product ID" field
    And I should see "Up sell" in the "Type" dropdown
    And I should see "True" in the "Liked" dropdown

Scenario: List all recommendations
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "100" in the results
    And I should see "200" in the results
    And I should not see "999" in the results

Scenario: Read a Recommendation
    When I visit the "Home Page"
    And I set the "Product ID" to "400"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "400" in the "Product ID" field
    And I should see "401" in the results
    When I copy the "Recommendation ID" field
    And I press the "Clear" button
    Then the "Recommendation ID" field should be empty
    And the "Product ID" field should be empty
    And the "Recommended product ID" field should be empty
    When I paste the "Recommendation ID" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "400" in the "Product ID" field
    And I should see "401" in the "Recommended product ID" field
    And I should see "Accessory" in the "Type" dropdown
    And I should see "True" in the "Liked" dropdown

Scenario: Search for cross-sell recommendations
    When I visit the "Home Page"
    And I select "Cross sell" in the "Type" dropdown
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "100" in the results
    And I should see "200" in the results
    And I should not see "300" in the results
    And I should not see "400" in the results

Scenario: Search for liked recommendations
    When I visit the "Home Page"
    And I select "True" in the "liked" dropdown
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "102" in the results
    And I should see "401" in the results
    And I should not see "101" in the results
    And I should not see "201" in the results
    And I should not see "301" in the results

Scenario: Delete a Recommendation
    When I visit the "Home Page"
    And I set the "Product ID" to "1000"
    And I set the "Recommended product ID" to "1001"
    And I select "Up sell" in the "Type" dropdown
    And I select "True" in the "Liked" dropdown
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Recommendation ID" field
    And I press the "Clear" button
    Then the "Recommendation ID" field should be empty
    And the "Product ID" field should be empty
    And the "Recommended product ID" field should be empty
    When I press the "Search" button
    Then I should see the message "Success"
    And I should see "1000" in the results
    When I press the "Clear" button
    Then the "Recommendation ID" field should be empty
    And the "Product ID" field should be empty
    And the "Recommended product ID" field should be empty
    When I paste the "Recommendation ID" field
    And I press the "Delete" button
    And I press the "Search" button
    Then I should see the message "Success"
    And I should not see "1000" in the results

Scenario: Update a Recommendation
    When I visit the "Home Page"
    And I set the "Product ID" to "2000"
    And I set the "Recommended product ID" to "2001"
    And I select "Up sell" in the "Type" dropdown
    And I select "True" in the "Liked" dropdown
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Recommendation ID" field
    And I press the "Clear" button
    Then the "Recommendation ID" field should be empty
    And the "Product ID" field should be empty
    And the "Recommended product ID" field should be empty
    When I press the "Search" button
    Then I should see the message "Success"
    And I should see "2000" in the results
    When I press the "Clear" button
    Then the "Recommendation ID" field should be empty
    And the "Product ID" field should be empty
    And the "Recommended product ID" field should be empty
    When I paste the "Recommendation ID" field
    When I press the "Retrieve" button
    Then I should see "2000" in the "Product ID" field
    And I should see "2001" in the "Recommended product ID" field
    And I should see "Up sell" in the "Type" dropdown
    And I should see "True" in the "Liked" dropdown
    When I set the "Recommended product ID" to "2002"
    And I select "Cross sell" in the "Type" dropdown
    And I press the "Update" button
    Then I should see the message "Success"
    When I copy the "Recommendation ID" field
    When I press the "Clear" button
    When I paste the "Recommendation ID" field
    When I press the "Retrieve" button
    Then I should see "2000" in the "Product ID" field
    And I should see "2002" in the "Recommended product ID" field
    And I should see "Cross sell" in the "Type" dropdown
    And I should see "True" in the "Liked" dropdown

Scenario: Like a Recommendation
    When I visit the "Home Page"
    And I set the "Product ID" to "200"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "200" in the "Product ID" field
    And I should see "201" in the "Recommended product ID" field
    And I should see "False" in the "Liked" dropdown
    Then I should see the message "Success"
    When I press the "Like" button
    And I copy the "Recommendation ID" field
    And I press the "Clear" button
    And I paste the "Recommendation ID" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "True" in the "Liked" dropdown

Scenario: Unlike a Recommendation
    When I visit the "Home Page"
    And I set the "Product ID" to "400"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "400" in the "Product ID" field
    And I should see "401" in the "Recommended product ID" field
    And I should see "True" in the "Liked" dropdown
    Then I should see the message "Success"
    When I press the "Unlike" button
    And I copy the "Recommendation ID" field
    And I press the "Clear" button
    And I paste the "Recommendation ID" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "False" in the "Liked" dropdown
