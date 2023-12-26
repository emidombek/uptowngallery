function saveEdit(field) {
  let inputId = `${field}Input`;
  let newValue = document.getElementById(inputId).value;

  // Construct the data to send in the AJAX request
  let data = {
    'field': field,
    'value': newValue,
    'csrfmiddlewaretoken': getCookie('csrftoken') // Getting the CSRF token
  };

  // Perform the AJAX request to the server
  fetch('/update_profile/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': getCookie('csrftoken')
      },
      body: new URLSearchParams(data)
    })
    .then(response => response.json())
    .then(data => {
      // Check the server response
      if (data.status === 'success') {
        // Successfully updated the profile
        toggleBackToText(field, newValue);
      } else {
        // Handle failure
        console.error('Failed to update:', data.error);
      }
    });
}

// Helper function to get CSRF token from cookies
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// This function is called after a successful AJAX response
function toggleBackToText(field, newValue) {
  let textId = `${field}Text`;
  let editIconId = `edit${field.charAt(0).toUpperCase() + field.slice(1)}Icon`;
  let saveIconId = `save${field.charAt(0).toUpperCase() + field.slice(1)}Icon`;

  // Update the text display
  document.getElementById(textId).textContent = newValue;
  document.getElementById(textId).style.display = 'inline';
  document.getElementById(`${field}Input`).style.display = 'none';
  document.getElementById(editIconId).style.display = 'inline';
  document.getElementById(saveIconId).style.display = 'none';
}