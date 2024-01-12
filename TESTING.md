## Validation:
### HTML Validation:

- [Full HTML Validation Report](docs/HTMLValidation.pdf)

- No errors or warnings were found when passing through the official [W3C](https://validator.w3.org/) validator by copying the copy from the page source. 

### CSS Validation:

- [Full CSS Validation Report](docs/CSSvalidation.pdf)

- No errors or warnings were found when passing through the official [W3C (Jigsaw)](https://jigsaw.w3.org/css-validator/#validate_by_uri).

### JS Validation:

- [Full JS Validation Report](docs/JSvalidation.pdf)

- No errors or warning messages were found when passing through the official [JSHint](https://www.jshint.com/) validator. 

### Python Validation:

- [Full Python Validation Report](docs/PythonValidation.pdf)

- No errors were found when the code was passed through CI's [online validation tool](https://pep8ci.herokuapp.com/).According to the reports, the code is [Pep 8-compliant](https://legacy.python.org/dev/peps/pep-0008/).
  
## Manual Testing

### Index Page

| Test Case ID | Description                              | Expected Result                                                                 | Actual Result     | Pass/Fail | Comments |
| ------------ | ---------------------------------------- | ------------------------------------------------------------------------------- | ----------------- | --------- | -------- |
| 1            | Page Load Test                           | The page loads without any errors and displays all content correctly.           | Expected Behavior | Pass      |          |
| 2            | Navigation Test to Painting Category     | Clicking on "Paintings" navigates to the correct category page.                 | Expected Behavior | Pass      |          |
| 3            | Image Loading for Paintings              | The image for the Paintings category loads correctly and is visible.            | Expected Behavior | Pass      |          |
| 4            | Alt Text Verification for Paintings      | The alt text for the Paintings image is correct and descriptive.                | Expected Behavior | Pass      |          |
| 5            | Navigation Test to Sculpture Category    | Clicking on "Sculpture" navigates to the correct category page.                 | Expected Behavior | Pass      |          |
| 6            | Image Loading for Sculpture              | The image for the Sculpture category loads correctly and is visible.            | Expected Behavior | Pass      |          |
| 7            | Alt Text Verification for Sculpture      | The alt text for the Sculpture image is correct and descriptive.                | Expected Behavior | Pass      |          |
| 8            | Responsiveness on Mobile Devices         | The webpage layout adjusts correctly when viewed on mobile devices.             | Expected Behavior | Pass      |          |
| 9            | Accessibility Check                      | All links are accessible with keyboard navigation.                              | Expected Behavior | Pass      |          |
| 10           | Browser Compatibility                    | The page renders correctly in different browsers (Chrome, Firefox, Safari).     | Expected Behavior | Pass      |          |
| 11           | Link Functionality for Other Categories  | All category links (Photography, Posters, Portraits, etc.) work correctly.      | Expected Behavior | Pass      |          |
| 12           | Image Loading for All Categories         | All category images load correctly and are visible.                             | Expected Behavior | Pass      |          |
| 13           | Alt Text Verification for All Categories | Alt text for each category image is correct and descriptive.                    | Expected Behavior | Pass      |          |
| 14           | Error Handling                           | The page shows appropriate messages or behavior on failed load or broken links. | Expected Behavior | Pass      |          |
| 15           | Loading Performance                      | The page and its elements load within a reasonable time frame.                  | Expected Behavior | Pass      |          |

### Navigation + Footer

| Test Case ID | Description                          | Expected Result                                                                                                | Actual Result     | Pass/Fail | Comments |
| ------------ | ------------------------------------ | -------------------------------------------------------------------------------------------------------------- | ----------------- | --------- | -------- |
| 1            | Page Load Test                       | The page loads without any errors and displays all content, including the header and footer.                   | Expected Behavior | Pass      |          |
| 2            | Main Navigation Functionality        | All main navigation links (Home, Profile, Browse Art, About) work correctly.                                   | Expected Behavior | Pass      |          |
| 3            | Authentication Links Visibility      | Authentication-related links (Login, Logout, Sign-up) are displayed based on the user's authentication status. | Expected Behavior | Pass      |          |
| 4            | Dropdown Menus in Navigation         | Dropdown menus for Profile and Browse Art work correctly and show options on click.                            | Expected Behavior | Pass      |          |
| 5            | Art Category Links Functionality     | All links in the Browse Art dropdown navigate to the correct categories.                                       | Expected Behavior | Pass      |          |
| 6            | Responsive Navbar                    | The navbar collapses and expands correctly in mobile view.                                                     | Expected Behavior | Pass      |          |
| 7            | Main Image Display                   | The main cover image is displayed correctly and is responsive.                                                 | Expected Behavior | Pass      |          |
| 8            | Search Functionality                 | The search bar functions correctly, accepting input and submitting queries.                                    | Expected Behavior | Pass      |          |
| 9            | Footer Social Media Links            | All social media links in the footer are clickable and navigate to the correct URLs.                           | Expected Behavior | Pass      |          |
| 10           | Favicon Visibility                   | Favicons are correctly displayed in the browser tab.                                                           | Expected Behavior | Pass      |          |
| 11           | Accessibility Check                  | All interactive elements are accessible via keyboard navigation.                                               | Expected Behavior | Pass      |          |
| 12           | Page Rendering in Different Browsers | The page renders correctly in different browsers (Chrome, Firefox, Safari, Edge).                              | Expected Behavior | Pass      |          |
| 13           | External CSS and JS Loading          | All external CSS and JavaScript files are loaded without errors.                                               | Expected Behavior | Pass      |          |
| 14           | Footer Copyright Information         | Footer displays the correct copyright information.                                                             | Expected Behavior | Pass      |          |
| 15           | Meta Tags and Viewport Configuration | Meta tags are correctly configured for charset, viewport, and compatibility.                                   | Expected Behavior | Pass      |          |

### Signup

| Test Case ID | Description                      | Expected Result                                                                                                             | Actual Result     | Pass/Fail | Comments |
| ------------ | -------------------------------- | --------------------------------------------------------------------------------------------------------------------------- | ----------------- | --------- | -------- |
| 1            | Page Load Test                   | The signup page loads without any errors and displays all content correctly.                                                | Expected Behavior | Pass      |          |
| 2            | Form Field Visibility            | All form fields (Email, Password, Confirm Password, Name, Address, City, State, Country, Zipcode) are visible and editable. | Expected Behavior | Pass      |          |
| 3            | Form Submission with Valid Data  | Submitting the form with all valid data successfully creates a new account.                                                 | Expected Behavior | Pass      |          |
| 4            | Error Message on Invalid Email   | An error message is displayed if an invalid email is entered.                                                               | Expected Behavior | Pass      |          |
| 5            | Password Validation              | An error message is displayed if the password does not meet the required criteria.                                          | Expected Behavior | Pass      |          |
| 6            | Confirm Password Validation      | An error message is displayed if the confirm password does not match the password.                                          | Expected Behavior | Pass      |          |
| 7            | Mandatory Fields Check           | An error message is displayed if any mandatory field is left empty.                                                         | Expected Behavior | Pass      |          |
| 8            | Responsive Layout Check          | The form layout is responsive and adjusts correctly on different screen sizes.                                              | Expected Behavior | Pass      |          |
| 9            | Submit Button Functionality      | The submit button works correctly and shows appropriate feedback when clicked.                                              | Expected Behavior | Pass      |          |
| 10           | Redirect After Successful Signup | The user is redirected to the appropriate page after successful signup.                                                     | Expected Behavior | Pass      |          |
| 11           | CSRF Token Validation            | Form submission validates the CSRF token correctly for security.                                                            | Expected Behavior | Pass      |          |
| 12           | Accessibility Check              | All form fields and the submit button are accessible with keyboard navigation.                                              | Expected Behavior | Pass      |          |
| 13           | Data Persistence Check           | Entered data persists in the fields when an error message is shown.                                                         | Expected Behavior | Pass      |          |
| 14           | Error Display for Each Field     | Each field shows its specific error message when data is invalid.                                                           | Expected Behavior | Pass      |          |
| 15           | Form Reset Functionality         | The form can be reset/cleared if needed.                                                                                    | Expected Behavior | Pass      |          |
 
 ### Login + Logout

 | Test Case ID | Description | Expected Result | Actual Result | Pass/Fail | Comments |
|--------------|-------------|-----------------|---------------|-----------|----------|
| 1 | Page Load Test for Login | The login page loads without any errors and displays all content correctly. | Expected Behavior | Pass | |
| 2 | Login Form Submission with Valid Credentials | Submitting the login form with valid credentials successfully logs in the user. | Expected Behavior | Pass | |
| 3 | Error Message on Invalid Credentials | An error message is displayed if the login credentials are invalid. | Expected Behavior | Pass | |
| 4 | 'Remember Me' Functionality | The 'Remember Me' checkbox functions correctly and retains user login status. | Expected Behavior | Pass | |
| 5 | Password Visibility Toggle | The password field allows toggling visibility of the entered password. | Expected Behavior | Pass | |
| 6 | 'Forgot Your Password' Link Functionality | The 'Forgot Your Password' link redirects to the password reset page. | Expected Behavior | Pass | |
| 7 | CSRF Token Validation | Form submission validates the CSRF token correctly for security. | Expected Behavior | Pass | |
| 8 | Redirect After Successful Login | The user is redirected to the appropriate page after successful login. | Expected Behavior | Pass | |
| 9 | Accessibility Check | All form fields and the submit button are accessible with keyboard navigation. | Expected Behavior | Pass | |
| 10 | Responsive Layout Check | The login form layout is responsive and adjusts correctly on different screen sizes. | Expected Behavior | Pass | |
| Test Case ID | Description | Expected Result | Actual Result | Pass/Fail | Comments |
|--------------|-------------|-----------------|---------------|-----------|----------|
| 1 | Page Load Test for Logout | The logout page loads without any errors and displays all content correctly. | Expected Behavior | Pass | |
| 2 | Logout Confirmation Message Visibility | The page displays a confirmation message asking if the user is sure they want to log out. | Expected Behavior | Pass | |
| 3 | Logout Process | Clicking the 'Sign Out' button successfully logs out the user. | Expected Behavior | Pass | |
| 4 | Redirect After Successful Logout | The user is redirected to the appropriate page after successful logout. | Expected Behavior | Pass | |
| 5 | CSRF Token Validation | Form submission validates the CSRF token correctly for security. | Expected Behavior | Pass | |
| 6 | Accessibility Check | The 'Sign Out' button is accessible with keyboard navigation. | Expected Behavior | Pass | |
| 7 | Responsive Layout Check | The logout form layout is responsive and adjusts correctly on different screen sizes. | Expected Behavior | Pass | |

### Profile Info (Upate Name + Address

| Test Case ID | Description                                     | Expected Result                                                                                   | Actual Result     | Pass/Fail | Comments |
| ------------ | ----------------------------------------------- | ------------------------------------------------------------------------------------------------- | ----------------- | --------- | -------- |
| 1            | Page Load Test                                  | The Profile page loads without any errors and displays the user's profile information.            | Expected Behavior | Pass      |          |
| 2            | Profile Image Display                           | The profile image is displayed correctly with appropriate alt text.                               | Expected Behavior | Pass      |          |
| 3            | Name Display and Edit Functionality             | The user's name is correctly displayed and can be edited using the edit/save icons.               | Expected Behavior | Pass      |          |
| 4            | Shipping Address Display and Edit Functionality | The shipping address is correctly displayed and can be edited using the edit/save icons.          | Expected Behavior | Pass      |          |
| 5            | Account Creation Date Display                   | The account creation date is correctly displayed in a readable format.                            | Expected Behavior | Pass      |          |
| 6            | Edit Functionality Validation                   | Edited information is validated and saved correctly when the save icon is clicked.                | Expected Behavior | Pass      |          |
| 7            | Responsive Layout Check                         | The page layout is responsive and adjusts correctly on different screen sizes.                    | Expected Behavior | Pass      |          |
| 8            | Accessibility Check                             | All interactive elements (edit/save icons, input fields) are accessible with keyboard navigation. | Expected Behavior | Pass      |          |
| 9            | Error Handling and User Feedback                | Appropriate error messages or feedback are displayed if an edit operation fails.                  | Expected Behavior | Pass      |          |
| 10           | Profile Information Consistency                 | Profile information updates are consistent and reflect across the site after editing.             | Expected Behavior | Pass      |          |
| 11           | Navigation Consistency                          | Navigation to and from the Profile page is consistent and maintains the application's state.      | Expected Behavior | Pass      |          |
| 12           | Cross-Browser Compatibility                     | The page renders correctly in different browsers (Chrome, Firefox, Safari, Edge).                 | Expected Behavior | Pass      |          |
| 13           | Security Checks                                 | User-specific information is secure, and the edit functionality is not accessible by other users. | Expected Behavior | Pass      |          |
| 14           | JavaScript Functionality                        | JavaScript functions for editing (toggleEdit, saveEdit) work correctly without errors.            | Expected Behavior | Pass      |          |
| 15           | Image Loading Performance                       | The profile image loads within a reasonable time frame and does not affect page performance.      | Expected Behavior | Pass      |          |
)

### Create Artwork

| Test Case ID | Description                           | Expected Result                                                                              | Actual Result     | Pass/Fail | Comments |
| ------------ | ------------------------------------- | -------------------------------------------------------------------------------------------- | ----------------- | --------- | -------- |
| 1            | Page Load Test                        | The Create Artwork Listing page loads without any errors and displays all content correctly. | Expected Behavior | Pass      |          |
| 2            | Title Field Functionality             | The Title field accepts input and validates it according to the specified criteria.          | Expected Behavior | Pass      |          |
| 3            | Description Field Functionality       | The Description field accepts input and validates it according to the specified criteria.    | Expected Behavior | Pass      |          |
| 4            | Image Upload Functionality            | The Image upload field accepts and validates image files correctly.                          | Expected Behavior | Pass      |          |
| 5            | Category Selection Functionality      | The Category dropdown works correctly and allows selection of a category.                    | Expected Behavior | Pass      |          |
| 6            | Reserve Price Field Functionality     | The Reserve Price field accepts numeric input and validates it correctly.                    | Expected Behavior | Pass      |          |
| 7            | Auction Duration Selection            | The Auction Duration field works correctly and validates the selected duration.              | Expected Behavior | Pass      |          |
| 8            | Form Submission with Valid Data       | Submitting the form with all valid data successfully creates an artwork listing.             | Expected Behavior | Pass      |          |
| 9            | Error Handling on Invalid Data        | The form displays appropriate error messages for invalid or incomplete fields.               | Expected Behavior | Pass      |          |
| 10           | Form Reset Functionality              | The form can be reset or cleared if needed.                                                  | Expected Behavior | Pass      |          |
| 11           | Confirmation Message After Submission | A confirmation or instruction message appears after successful form submission.              | Expected Behavior | Pass      |          |
| 12           | CSRF Token Validation                 | Form submission validates the CSRF token correctly for security.                             | Expected Behavior | Pass      |          |
| 13           | Responsive Layout Check               | The form layout is responsive and adjusts correctly on different screen sizes.               | Expected Behavior | Pass      |          |
| 14           | Accessibility Check                   | All form fields, buttons, and links are accessible with keyboard navigation.                 | Expected Behavior | Pass      |          |
| 15           | Help Text Visibility                  | Help text for each field is visible and provides adequate guidance.                          | Expected Behavior | Pass      |          |

### Pending Artwork (Edit or Delete)

| Test Case ID | Description                      | Expected Result                                                                                   | Actual Result     | Pass/Fail | Comments |
| ------------ | -------------------------------- | ------------------------------------------------------------------------------------------------- | ----------------- | --------- | -------- |
| 1            | Page Load Test                   | The Pending Artworks page loads without any errors and displays all listed artworks.              | Expected Behavior | Pass      |          |
| 2            | Artwork Display                  | Each artwork is displayed with its image, title, artist's name, description, and approval status. | Expected Behavior | Pass      |          |
| 3            | Image Visibility and Correctness | Artwork images are visible and correspond to their respective titles and descriptions.            | Expected Behavior | Pass      |          |
| 4            | Edit Button Functionality        | The 'Edit' button for each artwork redirects to the correct edit page.                            | Expected Behavior | Pass      |          |
| 5            | Delete Button Functionality      | The 'Delete' button removes the artwork from the pending list upon confirmation.                  | Expected Behavior | Pass      |          |
| 6            | CSRF Token Validation            | Form submissions for edit and delete validate the CSRF token correctly for security.              | Expected Behavior | Pass      |          |
| 7            | Confirmation Message on Deletion | A confirmation message or prompt appears when deleting an artwork.                                | Expected Behavior | Pass      |          |
| 8            | Responsive Layout Check          | The page layout is responsive and adjusts correctly on different screen sizes.                    | Expected Behavior | Pass      |          |
| 9            | Accessibility Check              | All interactive elements (edit and delete buttons) are accessible with keyboard navigation.       | Expected Behavior | Pass      |          |
| 10           | No Artwork Case Handling         | If no artworks are pending, an appropriate message or indication is displayed.                    | Expected Behavior | Pass      |          |
| 11           | Pagination Functionality         | If applicable, pagination controls function correctly and display additional artworks.            | Expected Behavior | Pass      |          |
| 12           | Error Handling                   | Appropriate error handling and user feedback are provided for any failed actions.                 | Expected Behavior | Pass      |          |
| 13           | Artwork Approval Status Display  | The approval status for each artwork is displayed correctly.                                      | Expected Behavior | Pass      |          |
| 14           | Refresh Reflects Changes         | The page reflects updates immediately after editing or deleting an artwork.                       | Expected Behavior | Pass      |          |
| 15           | Navigation Consistency           | Navigation to and from the page is consistent and maintains the application's state.              | Expected Behavior | Pass      |          |
| Test Case ID | Description | Expected Result | Actual Result | Pass/Fail | Comments |
|--------------|-------------|-----------------|---------------|-----------|----------|
| 1 | Page Load Test | The Edit Artwork page loads without any errors and displays the selected artwork's details for editing. | Expected Behavior | Pass | |
| 2 | Form Fields Population | All form fields are pre-populated with the current details of the artwork. | Expected Behavior | Pass | |
| 3 | Title Field Editability | The Title field can be edited and accepts new input. | Expected Behavior | Pass | |
| 4 | Description Field Editability | The Description field can be edited and accepts new input. | Expected Behavior | Pass | |
| 5 | Image Update Functionality | The Image field allows for uploading a new image and validates it correctly. | Expected Behavior | Pass | |
| 6 | Category Field Functionality | The Category field allows for selection change and reflects the update. | Expected Behavior | Pass | |
| 7 | Form Submission with Valid Data | Submitting the form with valid changes updates the artwork information. | Expected Behavior | Pass | |
| 8 | Error Handling on Invalid Data | The form displays appropriate error messages for invalid or incomplete fields. | Expected Behavior | Pass | |
| 9 | CSRF Token Validation | Form submission validates the CSRF token correctly for security. | Expected Behavior | Pass | |
| 10 | Confirmation Message After Submission | A confirmation message appears after successful submission indicating the update. | Expected Behavior | Pass | |
| 11 | Cancel Functionality | A 'Cancel' or 'Back' option is available and works correctly, discarding changes. | Expected Behavior | Pass | |
| 12 | Responsive Layout Check | The form layout is responsive and adjusts correctly on different screen sizes. | Expected Behavior | Pass | |
| 13 | Accessibility Check | All form fields, buttons, and links are accessible with keyboard navigation. | Expected Behavior | Pass | |
| 14 | Navigation Consistency | Navigation to and from the page is consistent and maintains the application's state. | Expected Behavior | Pass | |
| 15 | Refresh Reflects Changes | The page reflects updates immediately after successful submission. | Expected Behavior | Pass | |

### Art List & Auction Details Modal

| Test Case ID | Description                      | Expected Result                                                                                           | Actual Result     | Pass/Fail | Comments |
| ------------ | -------------------------------- | --------------------------------------------------------------------------------------------------------- | ----------------- | --------- | -------- |
| 1            | Page Load Test                   | The Artwork List page loads without any errors and displays the artwork list or search results.           | Expected Behavior | Pass      |          |
| 2            | Artwork Display                  | Each artwork is displayed with its image and title.                                                       | Expected Behavior | Pass      |          |
| 3            | Image Visibility and Correctness | Artwork images are visible and correspond to their respective titles.                                     | Expected Behavior | Pass      |          |
| 4            | Modal Pop-up Functionality       | Clicking on an artwork opens a modal pop-up with detailed information.                                    | Expected Behavior | Pass      |          |
| 5            | Pagination Functionality         | Pagination controls function correctly, navigating between pages of artwork.                              | Expected Behavior | Pass      |          |
| 6            | Search Functionality             | The search feature returns correct results or an appropriate message for no results.                      | Expected Behavior | Pass      |          |
| 7            | Responsive Layout Check          | The page layout is responsive and adjusts correctly on different screen sizes.                            | Expected Behavior | Pass      |          |
| 8            | Accessibility Check              | All interactive elements (images, modal links, pagination links) are accessible with keyboard navigation. | Expected Behavior | Pass      |          |
| 9            | Error Handling                   | Appropriate error handling and user feedback are provided for any failed actions.                         | Expected Behavior | Pass      |          |
| 10           | No Artwork Case Handling         | An appropriate message is displayed if no artworks are found in the list or search results.               | Expected Behavior | Pass      |          |
| 11           | Modal Close Functionality        | The modal pop-up can be closed without issues, returning to the artwork list.                             | Expected Behavior | Pass      |          |
| 12           | URL Parameters Handling          | The page correctly handles URL parameters for searches and pagination.                                    | Expected Behavior | Pass      |          |
| 13           | Page Title and Headings Accuracy | The page title and headings accurately reflect the content (e.g., Search Results, Category Name).         | Expected Behavior | Pass      |          |
| 14           | Refresh Reflects Changes         | The page reflects any updates or changes immediately after actions like searching.                        | Expected Behavior | Pass      |          |
| 15           | Navigation Consistency           | Navigation to and from the page maintains the application's state and user experience.                    | Expected Behavior | Pass      |          |

| Test Case ID | Description                       | Expected Result                                                                                            | Actual Result     | Pass/Fail | Comments |
| ------------ | --------------------------------- | ---------------------------------------------------------------------------------------------------------- | ----------------- | --------- | -------- |
| 1            | Page Load Test                    | The Auction Detail page loads without any errors and displays all content correctly.                       | Expected Behavior | Pass      |          |
| 2            | Artwork Image Display             | The artwork image is displayed correctly with appropriate alt text.                                        | Expected Behavior | Pass      |          |
| 3            | Artwork Title Display             | The title of the artwork is displayed prominently.                                                         | Expected Behavior | Pass      |          |
| 4            | Artwork Details Display           | Details such as category, artist name, number of bids, and current price are correctly displayed.          | Expected Behavior | Pass      |          |
| 5            | View Auction Button Functionality | The 'View Auction' button redirects to the correct auction detail page.                                    | Expected Behavior | Pass      |          |
| 6            | Responsive Layout Check           | The page layout is responsive and adjusts correctly on different screen sizes.                             | Expected Behavior | Pass      |          |
| 7            | Accessibility Check               | All interactive elements (images, links) are accessible with keyboard navigation.                          | Expected Behavior | Pass      |          |
| 8            | Correct Data Retrieval            | The page correctly retrieves and displays data specific to the selected auction.                           | Expected Behavior | Pass      |          |
| 9            | Error Handling                    | Appropriate error handling and user feedback are provided for any failed actions or data retrieval issues. | Expected Behavior | Pass      |          |
| 10           | Image Loading Performance         | The artwork image loads within a reasonable time frame and does not affect page performance.               | Expected Behavior | Pass      |          |
| 11           | Navigation Consistency            | Navigation to and from the page is consistent and maintains the application's state.                       | Expected Behavior | Pass      |          |
| 12           | URL Parameters Handling           | The page correctly handles URL parameters to display the appropriate auction details.                      | Expected Behavior | Pass      |          |
| 13           | Cross-Browser Compatibility       | The page renders correctly in different browsers (Chrome, Firefox, Safari, Edge).                          | Expected Behavior | Pass      |          |
| 14           | Refresh Reflects Changes          | Any updates or changes made in the auction are immediately reflected on the page.                          | Expected Behavior | Pass      |          |
| 15           | Overall User Experience           | The page provides a clear and user-friendly experience for viewing auction details.                        | Expected Behavior | Pass      |          |

### Auction Details Page with Bidding Functionality

| Test Case ID | Description                        | Expected Result                                                                                                                        | Actual Result     | Pass/Fail | Comments |
| ------------ | ---------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- | ----------------- | --------- | -------- |
| 1            | Page Load Test                     | The Auction Detail page loads without any errors and displays all content correctly.                                                   | Expected Behavior | Pass      |          |
| 2            | Artwork Image Display              | The artwork image is displayed correctly with appropriate alt text.                                                                    | Expected Behavior | Pass      |          |
| 3            | Artwork Details Display            | Details such as description, auction start and end dates, category, artist, number of bids, and current price are correctly displayed. | Expected Behavior | Pass      |          |
| 4            | Bid Submission Form Visibility     | The bid submission form is visible and accessible to authenticated users (excluding the artwork's artist).                             | Expected Behavior | Pass      |          |
| 5            | Form Field Validation              | The bid amount field validates the input correctly and shows feedback.                                                                 | Expected Behavior | Pass      |          |
| 6            | Submit Bid Functionality           | Submitting a valid bid updates the auction details and bid count appropriately.                                                        | Expected Behavior | Pass      |          |
| 7            | CSRF Token Validation              | Form submission validates the CSRF token correctly for security.                                                                       | Expected Behavior | Pass      |          |
| 8            | Responsive Layout Check            | The page layout is responsive and adjusts correctly on different screen sizes.                                                         | Expected Behavior | Pass      |          |
| 9            | User Authentication Handling       | The bid submission form is correctly hidden from unauthenticated users and the artwork's artist.                                       | Expected Behavior | Pass      |          |
| 10           | Error and Success Messages Display | Appropriate success or error messages are displayed after bid submission or other actions.                                             | Expected Behavior | Pass      |          |
| 11           | Accessibility Check                | All interactive elements (form fields, buttons, links) are accessible with keyboard navigation.                                        | Expected Behavior | Pass      |          |
| 12           | Navigation Consistency             | Navigation to and from the page is consistent and maintains the application's state.                                                   | Expected Behavior | Pass      |          |
| 13           | Image Loading Performance          | The artwork image loads within a reasonable time frame and does not affect page performance.                                           | Expected Behavior | Pass      |          |
| 14           | Cross-Browser Compatibility        | The page renders correctly in different browsers (Chrome, Firefox, Safari, Edge).                                                      | Expected Behavior | Pass      |          |
| 15           | Auction Timing Display Accuracy    | Auction start and end times are displayed accurately according to the server's time zone.                                              | Expected Behavior | Pass      |          |

### User Activity Dashboard (Artist Delete Closed Auctions)

| Test Case ID | Description                               | Expected Result                                                                                              | Actual Result     | Pass/Fail | Comments |
| ------------ | ----------------------------------------- | ------------------------------------------------------------------------------------------------------------ | ----------------- | --------- | -------- |
| 1            | Page Load Test                            | The Activity Dashboard page loads without any errors and displays all content correctly.                     | Expected Behavior | Pass      |          |
| 2            | Bidding Activity Accordion Functionality  | The Bidding Activity accordion expands and collapses correctly, showing the user's bidding history.          | Expected Behavior | Pass      |          |
| 3            | Selling Activity Accordion Functionality  | The Selling Activity accordion expands and collapses correctly, showing the user's selling history.          | Expected Behavior | Pass      |          |
| 4            | Active Auctions Accordion Functionality   | The Active Auctions accordion expands and collapses correctly, showing current active auctions.              | Expected Behavior | Pass      |          |
| 5            | Closed Auctions Accordion Functionality   | The Closed Auctions accordion expands and collapses correctly, showing the user's past auctions.             | Expected Behavior | Pass      |          |
| 6            | Auction Detail Links                      | Links to auction details navigate correctly to the respective auction pages.                                 | Expected Behavior | Pass      |          |
| 7            | Responsive Layout Check                   | The page layout is responsive and adjusts correctly on different screen sizes.                               | Expected Behavior | Pass      |          |
| 8            | No Activity Message Display               | Appropriate messages are displayed if no activity is found in any section.                                   | Expected Behavior | Pass      |          |
| 9            | Deletion Functionality in Closed Auctions | The delete button in Closed Auctions functions correctly, with a confirmation prompt.                        | Expected Behavior | Pass      |          |
| 10           | Accessibility Check                       | All interactive elements (accordion buttons, links, delete buttons) are accessible with keyboard navigation. | Expected Behavior | Pass      |          |
| 11           | Error Handling                            | Appropriate error handling and user feedback are provided for any failed actions.                            | Expected Behavior | Pass      |          |
| 12           | Cross-Browser Compatibility               | The page renders correctly in different browsers (Chrome, Firefox, Safari, Edge).                            | Expected Behavior | Pass      |          |
| 13           | Data Consistency                          | The displayed activities (bidding, selling, auctions) correctly reflect the user's actual activities.        | Expected Behavior | Pass      |          |
| 14           | Security Checks                           | User-specific information is secure, and other users cannot access or alter it.                              | Expected Behavior | Pass      |          |
| 15           | Overall User Experience                   | The page provides a clear and user-friendly experience for viewing various activities.                       | Expected Behavior | Pass      |          |

### About Page

| Test Case ID | Description                       | Expected Result                                                                                         | Actual Result     | Pass/Fail | Comments |
| ------------ | --------------------------------- | ------------------------------------------------------------------------------------------------------- | ----------------- | --------- | -------- |
| 1            | Page Load Test                    | The About Uptown Art Gallery page loads without any errors and displays all content correctly.          | Expected Behavior | Pass      |          |
| 2            | Main Heading Display              | The main heading "About Uptown Art Gallery" is displayed prominently.                                   | Expected Behavior | Pass      |          |
| 3            | Lead Text Display                 | The lead text under the main heading is displayed and clearly readable.                                 | Expected Behavior | Pass      |          |
| 4            | Gallery Image Display             | The gallery image is displayed correctly with appropriate alt text.                                     | Expected Behavior | Pass      |          |
| 5            | Mission Statement Section         | The Mission Statement section is displayed with the heading and corresponding text.                     | Expected Behavior | Pass      |          |
| 6            | History Section                   | The History section is displayed with the heading and corresponding text.                               | Expected Behavior | Pass      |          |
| 7            | Art and Artists Section           | The Art and Artists section is displayed with the heading and corresponding text.                       | Expected Behavior | Pass      |          |
| 8            | Community Engagement Section      | The Community Engagement section is displayed with the heading and corresponding text.                  | Expected Behavior | Pass      |          |
| 9            | Visit Us and Location Information | The Visit Us section and gallery location details are displayed correctly.                              | Expected Behavior | Pass      |          |
| 10           | Social Media Link Functionality   | The social media link (scroll-to-footer icon) works correctly and navigates to the footer.              | Expected Behavior | Pass      |          |
| 11           | Responsive Layout Check           | The page layout is responsive and adjusts correctly on different screen sizes.                          | Expected Behavior | Pass      |          |
| 12           | Accessibility Check               | All text content and interactive elements are accessible with keyboard navigation.                      | Expected Behavior | Pass      |          |
| 13           | Cross-Browser Compatibility       | The page renders correctly in different browsers (Chrome, Firefox, Safari, Edge).                       | Expected Behavior | Pass      |          |
| 14           | Content Accuracy                  | All displayed information (mission, history, art forms, community programs) is accurate and up-to-date. | Expected Behavior | Pass      |          |
| 15           | Overall User Experience           | The page provides a clear and informative user experience about the Uptown Art Gallery.                 | Expected Behavior | Pass      |          |

## Python Testing 

- [Python Coverage Report](docs/CoverageReportforPython.pdf)

## Lighthouse Testing

- [Python Coverage Report](docs/CoverageReportforPython.pdf)
  
## Issues/Bugs

   ### Issues

  - I encountered lots of issues while trying to get Jest for Javascript testing to run on machine, I utlimately opted for extensive manual testing in the interests of time. Javascript is not a large part of this project therefore manually testing the functionality should be sufficent. 

  - I orginally opted for Django Q as a way to have tasks running in the background to close the auctions on time but the elephant SQL kept getting overwhelmed with the connects despite limiting them. I had to scrap this idea in the end due to the database crashes it was causing. 
  
  - I was having isses with the bidding function where the amounts where not being recorded in decimal format, this was resolved by changing the data type to decimal in the Bids model for the amount field.

  - My commits where huge I found it very time consuming to make smaller commits and just kept forgetting as well to keep them smaller. I will realize this and will improve. 
  



   




