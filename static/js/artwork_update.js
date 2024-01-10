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
    'title': 'title',
    'description': 'description'
  };
  return fieldMapping[field] || field;
}

function saveEdit(field, artworkId) {
  let backendField = getBackendFieldName(field);
  let inputId = `${field}Input`;
  let newValue = document.getElementById(inputId).value;

  let data = {
    'artwork_id': artworkId,
    'field': backendField,
    'value': newValue,
    'csrfmiddlewaretoken': getCookie('csrftoken')
  };

  fetch('/pending_artworks/', {
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
    'title': 'title',
    'description': 'description'
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