/**
 This script dynamically updates the navigation bar to highlight the active link
 based on the current page URL. It runs on document ready and performs the following actions:
 
 Defines the `updateActiveNav` function to manage the active state of navigation links.
 It first removes the 'active' class from all navigation links.
 Then, it compares each navigation link's href attribute with the current window location.
 If a match is found, it adds the 'active' class to that link, highlighting it as active.
 
 Invokes the `updateActiveNav` function immediately to set the correct active link when the page loads.
 
 Binds the `updateActiveNav` function to the window's 'popstate' event.
 This ensures that the active link is updated correctly when navigating through browser history (back/forward buttons).
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

function getBackendFieldName(field) {
  const fieldMapping = {
    'name': 'name',
    'shippingAddress': 'shipping_address'
  };
  return fieldMapping[field] || field;
}

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
        toggleBackToText(field, newValue);
      } else {
        console.error('Failed to update:', data.error || 'Unknown error occurred');
      }
    })
    .catch(error => console.error('Fetch error:', error));
}

function getBackendFieldName(field) {
  const fieldMapping = {
    'name': 'name',
    'shippingAddress': 'shipping_address'
  };
  return fieldMapping[field] || field;
}

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