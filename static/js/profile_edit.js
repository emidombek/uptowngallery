/*
 Toggles the edit mode for a specified field by changing the display
of text, input elements, and edit/save icons.
 @param {string} field - The field to be toggled (e.g., 'name', 'address').
 */
function toggleEdit(field) {
  let textId = `${field}Text`;
  let inputId = `${field}Input`;
  let editIconId = `edit${field.charAt(0).toUpperCase() + field.slice(1)}Icon`;
  let saveIconId = `save${field.charAt(0).toUpperCase() + field.slice(1)}Icon`;

  document.getElementById(textId).style.display = 'none';
  document.getElementById(inputId).style.display = 'inline';
  document.getElementById(editIconId).style.display = 'none';
  document.getElementById(saveIconId).style.display = 'inline';
}
/*
 Maps a frontend field name to a corresponding backend field name.
 If no mapping is found, returns the original field name.
 @param {string} field - The frontend field name.
 @returns {string} The mapped backend field name.
 */
function getBackendFieldName(field) {
  const fieldMapping = {
    'name': 'name',
    'shippingAddress': 'shipping_address'
  };
  return fieldMapping[field] || field;
}
/**
 Saves the edited value of a field to the backend. Upon successful update,
 it toggles back to display the updated text and hides the input field.
 If the update fails, it logs the error.
 */
function saveEdit(field) {
  let backendField = getBackendFieldName(field);
  let inputId = `${field}Input`;
  let newValue = document.getElementById(inputId).value;

  let data = {
    'field': backendField,
    'value': newValue,
    'csrfmiddlewaretoken': getCookie('csrftoken')
  };

  fetch('/update_profile/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': getCookie('csrftoken')
      },
      body: new URLSearchParams(data)
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok: ' + response.statusText);
      }
      return response.json();
    })
    .then(data => {
      if (data.status === 'success') {
        window.location.reload(); // Reload the whole page to reflect changes
      } else {
        console.error('Failed to update:', data.message || 'Unknown error occurred');
      }
    })
    .catch(error => {
      console.error('Fetch error:', error);
    });
}
/**
 Retrieves the value of a specified cookie by its name.
 
 @param {string} name - The name of the cookie.
 @returns {string|null} The value of the cookie, or null if not found.
 */
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
/*
 Toggles back the display from edit mode to text mode after a field's 
 value has been successfully updated. It updates the text content and 
 adjusts the visibility of the edit and save icons.
 @param {string} field - The field that was edited.
 @param {string} newValue - The new value of the field to display.
 */
function toggleBackToText(field, newValue) {
  let textId = `${field}Text`;
  let editIconId = `edit${field.charAt(0).toUpperCase() + field.slice(1)}Icon`;
  let saveIconId = `save${field.charAt(0).toUpperCase() + field.slice(1)}Icon`;
  document.getElementById(textId).textContent = newValue;
  document.getElementById(textId).style.display = 'inline';
  document.getElementById(`${field}Input`).style.display = 'none';
  document.getElementById(editIconId).style.display = 'inline';
  document.getElementById(saveIconId).style.display = 'none';
}